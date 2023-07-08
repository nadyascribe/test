from __future__ import annotations


from sqlalchemy import select, update, func, or_, and_
from sqlalchemy.sql import Select

from dags.domain.attestations import (
    ContentType,
    EvidenceState,
    SignatureStatus,
    ContextType,
)
from dags.storage import get_session, get_engine
from dags.storage.models.osint import (
    Attestation,
    ComplianceRule,
)


def get_new_attestation_for_processing(
    content_types: list[ContentType | str],
    context_types: list[ContextType] | None = None,
    att_id: int | None = None,
) -> Select:
    q = (
        select(
            Attestation.id,
            Attestation.key,
            Attestation.contentType,
            Attestation.targetName,
            Attestation.teamId,
            Attestation.sigStatus,
        )
        .where(Attestation.contentType.in_(content_types))
        .where(Attestation.state == EvidenceState.UPLOADED)
        .where(
            or_(
                Attestation.sigStatus.is_(None),
                and_(
                    Attestation.sigStatus == SignatureStatus.IN_PROGRESS,
                    func.cardinality(Attestation.job_ids) == 0,
                ),
                and_(
                    Attestation.sigStatus == SignatureStatus.UNVERIFIED,
                    func.cardinality(Attestation.job_ids) == 1,  # one retry
                ),
            )
        )
    )

    if context_types:
        q = q.where(Attestation.contextType.in_(context_types))

    if att_id is not None:
        q = q.where(Attestation.id == att_id)

    return q


def set_attestation_job_id(attestation_id: int, run_id: str) -> None:
    eng = get_engine()
    eng.execute(
        update(Attestation)
        .where(Attestation.id == attestation_id)
        .values(job_ids=func.array_append(Attestation.job_ids, run_id))
    )


def change_attestation_sigstatus_by_key(att_key, state: SignatureStatus):
    if att_key is None:
        return
    eng = get_engine()
    eng.execute(update(Attestation).where(Attestation.key == att_key).values(sigStatus=state))


def change_attestation_state_by_ids(att_ids: list[int], state: SignatureStatus):
    if not att_ids:
        return
    eng = get_engine()
    eng.execute(update(Attestation).where(Attestation.id.in_(att_ids)).values(sigStatus=state))


def get_compliance_rules(rule_ids: list[str]) -> dict[str, ComplianceRule]:
    curs: list[ComplianceRule] = get_session().query(ComplianceRule).filter(ComplianceRule.ruleId.in_(rule_ids))
    res = {}
    for row in curs:
        res[row.ruleId] = row
    return res


def get_base_images(attestation_id: int, include_null_base: bool = False) -> list:
    q = f"""
        SELECT
            registry.id,
            registry.image_id,
            registry.repository,
            registry.tag,
            (SELECT count(*) FROM regexp_matches(sbom.s, ':', 'g')) AS total_layers,
            (SELECT count(*) FROM regexp_matches(sbom.s, ':', 'g')) -
            (SELECT count(*) FROM regexp_matches(ltrim(sbom.s, registry.s), ':', 'g')) 
            AS cutoff_layer
        FROM (
                SELECT *, rtrim(replace(config #>> '{{rootfs,diff_ids}}', ' ', ''), ']') AS s
                FROM osint."RegistryImage"
                WHERE is_base_image {include_null_base and 'IS DISTINCT FROM FALSE' or 'IS TRUE'}
            ) registry
            INNER JOIN (
                SELECT
                    a.context ->> 'imageID' AS image_id,
                    array_to_json(array_agg(c.info ->> 'name' ORDER BY ac.info ->> 'layer_number' ASC))::TEXT AS s
                FROM osint."Attestation" AS a
                    INNER JOIN osint."AttestationComponent" ac ON ac.attestation = a.id
                    INNER JOIN osint."Component" c ON ac.component = c.id
                WHERE c.group = 'layer' AND a.id = {attestation_id}
                GROUP BY image_id
            ) sbom
            ON sbom.s LIKE registry.s || '%'
            AND sbom.s != registry.s || ']'
    """
    base_images = list(get_engine().execute(q))
    return base_images
