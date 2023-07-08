import pytest

from airflow import DAG
from airflow.models import DagRun
from airflow.utils.state import DagRunState, State

from dags.storage.models.osint import (
    Component,
    VulAdvisory,
    VulComponent,
    Vulnerability,
)

vuln_ids = ["CVE-2010-1205", "CVE-2007-1667", "CVE-2010-5298"]


@pytest.fixture()
def components():
    return [
        Component(
            purl="pkg:deb/ubuntu/openssl@1.1.1f-1ubuntu2.17?arch=amd64&distro=ubuntu-20.04",
            cpes=["cpe:2.3:a:openssl:openssl:1.1.1f-1ubuntu2.17:*:*:*:*:*:*:*"],
            type="library",
            group="deb",
            name="openssl",
        ),
        Component(
            purl="pkg:alpine/busybox@1.35.0-r13?arch=aarch64&upstream=busybox&distro=alpine-3.16.0",
            cpes=["cpe:2.3:a:busybox:busybox:1.35.0-r13:*:*:*:*:*:*:*"],
            type="library",
            group="apk",
            name="busybox",
        ),
        Component(
            purl="pkg:npm/imagemagick@0.1.3",
            cpes=[
                "cpe:2.3:a:*:imagemagick:0.1.3:*:*:*:*:*:*:*",
                "cpe:2.3:a:imagemagick:imagemagick:0.1.4:*:*:*:*:*:*:*",
            ],
            type="library",
            group="npm",
            name="imagemagick",
        ),
    ]


@pytest.fixture()
def vulnerabilities():
    return [
        Vulnerability(id=vuln_ids[0], severity=1),
        Vulnerability(id=vuln_ids[1], severity=1),
        Vulnerability(id=vuln_ids[2], severity=1),
    ]


@pytest.fixture()
def vuln_advisories():
    return [
        VulAdvisory(
            vulId=vuln_ids[0],
            source="NVD3.1",
            cpes=[
                "cpe:2.3:a:libpng:libpng:*:*:*:*:*:*:*:*",
                "cpe:2.3:a:libpng:libpng:1.0:*:*:*:*:*:*:*",
            ],
        ),
        VulAdvisory(
            vulId=vuln_ids[1],
            source="NVD2",
            cpes=["cpe:2.3:a:openssl:openssl:*:*:*:*:*:*:*:*"],
        ),
        VulAdvisory(
            vulId=vuln_ids[2],
            source="NVD2",
            cpes=[
                "cpe:2.3:a:imagemagick:imagemagick:*:*:*:*:*:*:*:*",
                "cpe:2.3:a:x.org:libx11:*:*:*:*:*:*:*:*",
            ],
        ),
    ]


@pytest.fixture()
def dag(dagbag):
    d: DAG = dagbag.get_dag(dag_id="update_vuln_components")
    assert d is not None
    assert len(d.tasks) > 0
    return d


def db_cleanup(session):
    session.query(VulComponent).delete()
    session.query(Component).delete()
    session.query(VulAdvisory).delete()
    session.query(Vulnerability).delete()


# runs the dag and asserts all tasks succeeded
def run_dag(dag):
    dag.test()
    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS
    tis = dag_run.get_task_instances()
    assert all(ti.state == State.SUCCESS for ti in tis), [(ti.id, ti.state) for ti in tis]


# get component vulnerability mappings
def get_vuln_components(session):
    return (
        session.query(
            VulComponent.component,
            Vulnerability.id,
            VulComponent.created,
            VulComponent.deleted,
        )
        .join(Vulnerability, VulComponent.vulId == Vulnerability.id)
        .order_by(VulComponent.component, Vulnerability.id, VulComponent.created)
        .all()
    )


def test_empty_tables(dag, session, components, vulnerabilities, vuln_advisories):
    # no components or vulnerability advisories
    db_cleanup(session)
    session.commit()
    assert session.query(Component).count() == 0
    assert session.query(VulAdvisory).count() == 0
    assert session.query(VulComponent).count() == 0

    run_dag(dag)
    assert session.query(VulComponent).count() == 0

    # no vulnerability advisories
    session.add_all(components)
    session.commit()
    assert session.query(Component).count() == 3

    run_dag(dag)
    assert session.query(VulComponent).count() == 0

    # no components
    db_cleanup(session)
    session.add_all(vulnerabilities)
    session.flush()
    session.add_all(vuln_advisories)
    session.commit()
    assert session.query(VulAdvisory).count() == 3

    run_dag(dag)
    assert session.query(VulComponent).count() == 0


def test_vuln_components_modifications(dag, session, components, vulnerabilities, vuln_advisories):
    # seed DB
    db_cleanup(session)
    session.add_all(components)
    session.add_all(vulnerabilities)
    session.flush()
    session.add_all(vuln_advisories)
    session.commit()

    run_dag(dag)
    vuln_components = get_vuln_components(session)
    assert len(vuln_components) == 2
    # mapping of pkg:deb/ubuntu/openssl@1.1.1f-1ubuntu2.17?arch=amd64&distro=ubuntu-20.04 to CVE-2007-1667
    assert vuln_components[0].component == components[0].id
    assert vuln_components[0].id == vulnerabilities[1].id
    assert vuln_components[0].created != None
    assert vuln_components[0].deleted == None
    # mapping of pkg:npm/imagemagick@0.1.3 to CVE-2010-5298
    assert vuln_components[1].component == components[2].id
    assert vuln_components[1].id == vulnerabilities[2].id
    assert vuln_components[1].created != None
    assert vuln_components[1].deleted == None

    # add components
    components.extend(
        [
            Component(
                purl="pkg:deb/debian/openssl@1.1.1n-0+deb11u4?arch=amd64&distro=debian-11",
                cpes=["cpe:2.3:a:openssl:openssl:1.1.1n-0\\+deb11u4:*:*:*:*:*:*:*"],
                type="library",
                group="deb",
                name="openssl",
            ),
            Component(
                purl="pkg:npm/lodash@4.17.20",
                cpes=[
                    "cpe:2.3:a:*:lodash:4.17.20:*:*:*:*:*:*:*",
                    "cpe:2.3:a:lodash:lodash:4.17.20:*:*:*:*:*:*:*",
                ],
                type="library",
                group="npm",
                name="lodash",
            ),
        ]
    )

    session.add_all([components[3], components[4]])
    session.commit()

    run_dag(dag)
    vuln_components = get_vuln_components(session)
    assert len(vuln_components) == 3
    # mapping of pkg:deb/debian/openssl@1.1.1n-0+deb11u4?arch=amd64&distro=debian-11 to CVE-2007-1667
    assert vuln_components[2].component == components[3].id
    assert vuln_components[2].id == vulnerabilities[1].id
    assert vuln_components[2].created != None
    assert vuln_components[2].deleted == None

    # add vulnerabilities
    vuln_ids.extend(["CVE-2018-3721", "CVE-2010-2701", "CVE-2021-23337"])

    vulnerabilities.extend(
        [
            Vulnerability(id=vuln_ids[3], severity=1),
            Vulnerability(id=vuln_ids[4], severity=1),
            Vulnerability(id=vuln_ids[5], severity=1),
        ]
    )

    session.add_all([vulnerabilities[3], vulnerabilities[4], vulnerabilities[5]])
    session.flush()

    vuln_advisories.extend(
        [
            VulAdvisory(
                vulId=vuln_ids[3],
                source="NVD3",
                cpes=["cpe:2.3:a:lodash:lodash:4.17.20:*:*:*:*:node.js:*:*"],
            ),
            VulAdvisory(
                vulId=vuln_ids[4],
                source="NVD3",
                cpes=["cpe:2.3:a:fathsoft:fathftp:1.7:*:*:*:*:*:*:*"],
            ),
            VulAdvisory(
                vulId=vuln_ids[5],
                source="NVD3.1",
                cpes=["cpe:2.3:a:dash:lodash:*:*:*:*:*:node.js:*:*"],
            ),
        ]
    )

    session.add_all([vuln_advisories[3], vuln_advisories[4], vuln_advisories[5]])
    session.commit()

    run_dag(dag)
    vuln_components = get_vuln_components(session)
    assert len(vuln_components) == 5
    # mapping of pkg:npm/lodash@4.17.20 to CVE-2018-3721
    assert vuln_components[3].component == components[4].id
    assert vuln_components[3].id == vulnerabilities[3].id
    assert vuln_components[3].created != None
    assert vuln_components[3].deleted == None
    # mapping of pkg:npm/lodash@4.17.20 to CVE-2021-23337
    assert vuln_components[4].component == components[4].id
    assert vuln_components[4].id == vulnerabilities[5].id
    assert vuln_components[4].created != None
    assert vuln_components[4].deleted == None

    # modify component cpes
    components[4].cpes = cpes = [
        "cpe:2.3:a:*:lodash:4.17.20:*:*:*:*:node:*:*",
        "cpe:2.3:a:lodash:lodash:4.17.20:*:*:*:*:node.js:*:*",
    ]
    session.commit()

    run_dag(dag)
    vuln_components = get_vuln_components(session)
    assert len(vuln_components) == 5
    # mapping of pkg:npm/lodash@4.17.20 to CVE-2018-3721 remains
    assert vuln_components[3].component == components[4].id
    assert vuln_components[3].id == vulnerabilities[3].id
    assert vuln_components[3].created != None
    assert vuln_components[3].deleted == None
    # mapping of pkg:npm/lodash@4.17.20 to CVE-2021-23337 removed (logical delete)
    assert vuln_components[4].component == components[4].id
    assert vuln_components[4].id == vulnerabilities[5].id
    assert vuln_components[4].created != None
    assert vuln_components[4].deleted != None

    # modify vulnerability cpes
    vuln_advisories[1].cpes = ["cpe:2.3:a:openssl:openssl:1.1.1n-0\\+deb11u4:*:*:*:*:*:*:*"]
    vuln_advisories[5].cpes = ["cpe:2.3:a:lodash:lodash:*:*:*:*:*:node.js:*:*"]
    session.commit()

    run_dag(dag)
    vuln_components = get_vuln_components(session)
    assert len(vuln_components) == 6
    # mapping of pkg:deb/ubuntu/openssl@1.1.1f-1ubuntu2.17?arch=amd64&distro=ubuntu-20.04 to CVE-2007-1667 removed (logical delete)
    assert vuln_components[0].component == components[0].id
    assert vuln_components[0].id == vulnerabilities[1].id
    assert vuln_components[0].created != None
    assert vuln_components[0].deleted != None
    # mapping of pkg:deb/debian/openssl@1.1.1n-0+deb11u4?arch=amd64&distro=debian-11 to CVE-2007-1667 remains
    assert vuln_components[2].component == components[3].id
    assert vuln_components[2].id == vulnerabilities[1].id
    assert vuln_components[2].created != None
    assert vuln_components[2].deleted == None
    # old removed mapping of pkg:npm/lodash@4.17.20 to CVE-2021-23337 untouched
    assert vuln_components[4].component == components[4].id
    assert vuln_components[4].id == vulnerabilities[5].id
    assert vuln_components[4].created != None
    assert vuln_components[4].deleted != None
    # new mapping of pkg:npm/lodash@4.17.20 to CVE-2021-23337
    assert vuln_components[5].component == components[4].id
    assert vuln_components[5].id == vulnerabilities[5].id
    assert vuln_components[5].created != None
    assert vuln_components[5].deleted == None
