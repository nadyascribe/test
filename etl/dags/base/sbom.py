import json
import logging
import os.path
import typing

from airflow.decorators import task
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from dags.base import attestations as attestations_base
from dags.storage import get_engine, model_as_dict, make_upsert_query
from dags.storage.models import osint
from dags.storage.models.osint import ComponentType
from dags.storage.queries import vuln_advisories
from dags.tools import fs, grype

logger = logging.getLogger("airflow.task")


@task(task_id="extract_and_save_dependencies")
def extract_and_save_dependencies(att: attestations_base.AttestationResultDict, downloaded_attest_path: str) -> None:
    """
    Extracts all dependencies from sbom and store them into db.
    """
    with open(downloaded_attest_path, "rb") as file:
        data = json.load(file)
    with get_engine().connect() as connection:
        types = {r.enum for r in connection.execute(select(ComponentType.enum))}

        with connection.begin():
            # we need it to be sorted to prevent deadlocks
            for comp in sorted(data["components"], key=lambda c: c.get("purl", "")):
                try:
                    if comp["group"] not in types:
                        logger.warning("component type %s is not supported", comp["group"])
                        continue
                    cpes = set()
                    if comp.get("cpe") is not None:
                        cpes.add(comp["cpe"])
                    cpes.update(p["value"] for p in comp["properties"] if p["name"] == "cpe")
                    component = osint.Component(
                        purl=comp["purl"],
                        name=comp["name"],
                        group=comp["group"],
                        type=comp["type"],
                        cpes=list(cpes),
                        mainAttestation=None,
                        info=comp,
                        licenses=_get_component_licenses(comp),
                    )
                    res = connection.execute(
                        make_upsert_query(osint.Component, ["purl", "teamId"]).returning(osint.Component.id),
                        **model_as_dict(component),
                    )
                    component_id = res.fetchone().id
                    info = {}
                    for prop in comp.get("properties") or []:
                        name = prop.get("name")

                        if comp["group"] == "layer" and name == "index":
                            info["layer_number"] = prop["value"]

                        if name == "layer_ref":
                            info["layer_ref"] = prop["value"]
                        elif name == "importer-path":
                            info["importer_path"] = prop["value"]

                    att_component = osint.AttestationComponent(
                        attestation=int(att["id"]),
                        component=component_id,
                        info=info,
                    )
                    connection.execute(
                        insert(osint.AttestationComponent).values(model_as_dict(att_component)).on_conflict_do_nothing()
                    )
                except KeyError:
                    logger.warning("component %s is missing some fields", comp)


def _get_component_licenses(comp: dict) -> list[str]:
    res = []
    for l in comp.get("licenses") or []:
        lic = (l.get("license") or {}).get("name")
        if lic and lic.lower() not in ["and", "or"]:
            res.append(lic)
    return [l["license"]["name"] for l in (comp.get("licenses") or [])]


@task(task_id="run_grype_and_save_deps")
def run_grype_and_save_deps(att: attestations_base.AttestationResultDict, downloaded_attest_path: str) -> None:
    """
    Runs grype (vulnerabilities detector) and saves results into db.
    """
    output = f"{os.path.splitext(downloaded_attest_path)[0]}.grype.json"
    syft_path = grype.extract_syft(downloaded_attest_path)
    grype.run(syft_path, output)

    with open(output, "rb") as f:
        data = json.load(f)

    vuln_advisories.save_grype_report(data, int(att["id"]))
    fs.remove_file(output)
    fs.remove_file(syft_path)


def make_tasks(att: attestations_base.AttestationResultDict, downloaded_attest_path: str) -> list[typing.Any]:
    grype = run_grype_and_save_deps(att=att, downloaded_attest_path=downloaded_attest_path)
    extract = extract_and_save_dependencies(att=att, downloaded_attest_path=downloaded_attest_path)
    extract >> grype
    return [grype, extract]
