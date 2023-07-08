from datetime import datetime, timedelta
import pytest
from airflow import DAG
from airflow.models import DagRun
from airflow.utils.state import DagRunState, State

from dags.domain.advisory import AdvisoryType
from dags.storage.models.osint import VulAdvisory, Vulnerability


@pytest.fixture()
def dag(dagbag, session):
    d: DAG = dagbag.get_dag(dag_id="nvds_import")
    assert d is not None
    assert len(d.tasks) > 0
    yield d
    session.commit()


def cleanup(session):
    session.query(VulAdvisory).delete()
    session.query(Vulnerability).delete()


_last_modified = "2022-02-28T18:19:59.150"
_nvd_cve = {
    "cve": {
        "id": "CVE-2004-2260",
        "sourceIdentifier": "cve@mitre.org",
        "published": "2004-12-31T05:00:00.000",
        "lastModified": _last_modified,
        "vulnStatus": "Analyzed",
        "descriptions": [
            {
                "lang": "en",
                "value": "Opera Browser 7.23, and other versions before 7.50, updates the address bar as soon as the user clicks a link, which allows remote attackers to redirect to other sites via the onUnload attribute.",
            }
        ],
        "metrics": {
            "cvssMetricV2": [
                {
                    "source": "nvd@nist.gov",
                    "type": "Primary",
                    "cvssData": {
                        "version": "2.0",
                        "vectorString": "AV:N\/AC:L\/Au:N\/C:N\/I:P\/A:N",
                        "accessVector": "NETWORK",
                        "accessComplexity": "LOW",
                        "authentication": "NONE",
                        "confidentialityImpact": "NONE",
                        "integrityImpact": "PARTIAL",
                        "availabilityImpact": "NONE",
                        "baseScore": 5.0,
                    },
                    "baseSeverity": "MEDIUM",
                    "exploitabilityScore": 10.0,
                    "impactScore": 2.9,
                    "acInsufInfo": False,
                    "obtainAllPrivilege": False,
                    "obtainUserPrivilege": False,
                    "obtainOtherPrivilege": False,
                    "userInteractionRequired": False,
                }
            ]
        },
        "weaknesses": [
            {
                "source": "nvd@nist.gov",
                "type": "Primary",
                "description": [{"lang": "en", "value": "CWE-601"}],
            }
        ],
        "configurations": [
            {
                "nodes": [
                    {
                        "operator": "OR",
                        "negate": False,
                        "cpeMatch": [
                            {
                                "vulnerable": True,
                                "criteria": "cpe:2.3:a:opera:opera_browser:*:*:*:*:*:*:*:*",
                                "versionEndExcluding": "7.50",
                                "matchCriteriaId": "3C2A60B0-579A-46F8-91E4-63275CF8595A",
                            }
                        ],
                    }
                ]
            }
        ],
        "references": [
            {
                "url": "http:\/\/www.securityfocus.com\/bid\/10337",
                "source": "cve@mitre.org",
                "tags": ["Broken Link", "Patch", "Third Party Advisory", "VDB Entry"],
            },
            {
                "url": "https:\/\/exchange.xforce.ibmcloud.com\/vulnerabilities\/16131",
                "source": "cve@mitre.org",
                "tags": ["Third Party Advisory", "VDB Entry"],
            },
        ],
    }
}


def test_dag__empty_db(dag, session, mocker):
    cleanup(session)
    assert session.query(VulAdvisory).count() == 0
    assert session.query(Vulnerability).count() == 0
    with (
        mocker.patch("dags.nvd_import.nvd_service.download_cves", return_value=([_nvd_cve], 1)),
        mocker.patch(
            "dags.nvd_import.nvd_service.Params.prepare_for_next_request",
            return_value=False,
        ),
    ):
        dag.test()
    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS
    tis = dag_run.get_task_instances()
    assert all(ti.state == State.SUCCESS for ti in tis), [(ti.id, ti.state) for ti in tis]
    assert session.query(VulAdvisory).count() > 0
    assert session.query(Vulnerability).count() > 0


def test_dag__with_just_inserted_vulns(dag, session, mocker):
    cleanup(session)
    existed_vulns = [
        "CVE-2021-0001",
        "CVE-2021-0002",
    ]
    assert _nvd_cve["cve"]["id"] not in existed_vulns

    _date = datetime.fromisoformat(_last_modified)
    session.add_all(
        [
            Vulnerability(id=existed_vulns[0], severity=1),
            Vulnerability(id=existed_vulns[1], severity=1),
        ]
    )
    session.flush()
    session.add_all(
        [
            VulAdvisory(
                vulId=existed_vulns[0],
                source=AdvisoryType.NVD31,
                lastModified=_date,
                cpes=[],
            ),
            VulAdvisory(
                vulId=existed_vulns[1],
                source=AdvisoryType.NVD31,
                lastModified=_date,
                cpes=[],
            ),
        ]
    )
    session.commit()
    with (
        mocker.patch("dags.nvd_import.nvd_service.download_cves", return_value=([_nvd_cve], 1)),
        mocker.patch(
            "dags.nvd_import.nvd_service.Params.prepare_for_next_request",
            return_value=False,
        ),
    ):
        dag.test()
    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS
    tis = dag_run.get_task_instances()
    assert all(ti.state == State.SUCCESS for ti in tis), [(ti.id, ti.state) for ti in tis]
    assert session.query(VulAdvisory).count() > 0
    assert session.query(Vulnerability).count() > 0
