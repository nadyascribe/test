import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dags.storage import Attestation
from dags.storage import Vulnerability
from dags.storage import AttestationComponent
from dags.storage import Component
from dags.storage.models.osint import VulComponent
import os
import json
from sqlalchemy import create_engine
from sqlalchemy import desc
import subprocess
import time


DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = 5433
DB_USER = os.environ.get("DB_USER", "airflow")
DB_PASSWORD = os.environ.get("TEST_DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME", "airflow")
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
INSTANCE_ID = os.environ.get("INSTANCE_ID", "i-0d5abc7e5ea9a77fe")
AWS_HOST = os.environ.get("AWS_HOST", "scribe-test-airflow.cmftdcwhlzam.us-west-2.rds.amazonaws.com")


def create_ssh_tunnel_through_ssm(instance_id, local_port, remote_port):
    try:
        # Start the SSM session and establish a tunnel
        print("@@@@@@@@@ Starting SSM session...")

        ssm_tunnel = subprocess.Popen(
            [
                "/usr/local/bin/aws",
                "ssm",
                "start-session",
                "--target",
                instance_id,
                "--document-name",
                "AWS-StartPortForwardingSessionToRemoteHost",
                "--parameters",
                f'{{"host":["{AWS_HOST}"], "localPortNumber":["{local_port}"], "portNumber":["{remote_port}"]}}',
                "--region",
                AWS_REGION,
            ],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return ssm_tunnel
    except Exception as e:
        print("SSM session failed with error:", str(e))
        raise


@pytest.fixture(scope="session")
def sshTunnel():
    tunnel = create_ssh_tunnel_through_ssm(INSTANCE_ID, DB_PORT, 5432)
    try:
        print("@@@@@@@@@ Establishing SSH tunnel...")
        yield tunnel
    finally:
        # Close the tunnel after you are done
        # print("@@@@@@@@@ Killing SSH tunnel...")
        # os.killpg(os.getpgid(tunnel.pid), signal.SIGTERM)
        tunnel.kill()


@pytest.fixture(scope="session")
def mysession(sshTunnel):
    # Poll the output of the tunnel process
    print("@@@@@@@@@ Poll the output of the tunnel process...")
    while True:
        output = sshTunnel.stdout.readline()
        print(output.strip())
        if "Waiting for connections..." in output:
            print("@@@@@@@@@ SSM tunnel waiting for connections...")
            break

    # set up a database connection and a session
    # print(f'@@@@@@@ postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}')
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}")
    Session = sessionmaker(bind=engine)
    mysession = Session()
    yield mysession
    # tear down the session and the database connection
    mysession.close()


# fixture for pytest (used as global values for the tests) - gets all the component IDs of the uploaded attestation
@pytest.fixture(scope="session")
def component_ids(mysession):
    product_key = os.environ.get("PRODUCT_KEY", "automated_test_v0.2")
    id = get_uploaded_attestation_id(mysession, {"name": product_key})
    # if id is None: fail the pytest
    if id is None:
        print("No attestation ID found for the product key")
        pytest.fail("No attestation ID found for the product key", product_key)
    print("@@@@@@@@@ found attestation ID: ", id, " for product key: ", product_key)
    return get_component_ids_by_attestation_id(mysession, id)


def get_uploaded_attestation_id(mysession, search_params):
    for i in range(20):
        time.sleep(5 * i)
        attestation = (
            mysession.query(Attestation)
            .filter(Attestation.context.contains(search_params))
            .order_by(desc(Attestation.id))
            .first()
        )
        if attestation is not None:
            mysession.refresh(attestation)  # refresh the object
            if attestation.sigStatus == "verified":
                return attestation.id
            print(f"Found attestation id: {attestation.id}, sigStatus: {attestation.sigStatus}, retry number: {i}...")
        else:
            print(f"Did not find attestation for {search_params}, retry number: {i}...")
    return None


# Get all the component IDs of the attestation by querying the AttestationComponent table
def get_component_ids_by_attestation_id(mysession, attestation_id):
    if attestation_id is None:
        return None
    components = mysession.query(AttestationComponent).filter(AttestationComponent.attestation == attestation_id).all()
    return [component.component for component in components]


class ComponentTestClass(Component):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Test 1: Get all the components from the Component table and compare them to the expected fixture
def test_components_by_ids(mysession, component_ids):
    assert component_ids, "No component IDs found for the product key"

    db_components = mysession.query(ComponentTestClass).filter(ComponentTestClass.id.in_(component_ids)).all()

    # Create a list of component dictionaries
    components_list = [component.to_dict() for component in db_components]

    # # CREATING THE FIXTURES FILE, DONT DELETE
    # with open('components_list.json', 'w') as file:
    #     json.dump({"component_fixtures": components_list}, file, default=str)

    # Relative path to the fixture file (relative to the current script)
    relative_path = "fixtures/components_list.json"
    data = getFixturesFromFile(relative_path)

    # Iterate through the fixtures in the json and compare each fixture to a component with the same id
    for fixture in data["component_fixtures"]:
        if fixture["purl"].startswith("pkg:layer/index.docker.io/"):
            print("found a layer PURL, skipping...", fixture["purl"])
            continue

        purl_component = next((c for c in components_list if c["purl"] == fixture["purl"]), None)

        assert purl_component, f"No matching component found for fixture with purl: {fixture['purl']}"
        assert purl_component["purl"] == fixture["purl"]
        assert purl_component["teamId"] == fixture["teamId"]
        assert purl_component["type"] == fixture["type"]
        assert purl_component["group"] == fixture["group"]
        if len(fixture["cpes"]) > 0:
            assert len(purl_component["cpes"]) > 0
        # assert purl_component["cpes"] == fixture["cpes"]
        assert purl_component["name"] == fixture["name"]
        assert purl_component["mainAttestation"] == fixture["mainAttestation"]
        # assert purl_component["info"] == fixture["info"]
        assert purl_component["extraIdx"] == fixture["extraIdx"]
        assert purl_component["licenses"] == fixture["licenses"]
        # assert purl_component["txt"] == fixture["txt"]
        assert purl_component["version"] == fixture["version"]


# Gets all the vulnerability IDs of the components
@pytest.fixture
def vul_ids(mysession, component_ids):
    if component_ids is None:
        print("No component IDs found for the product key")
        pytest.fail("No component IDs found for the product key")
    print(
        "@@@@@@@@@ how many components were found - len(component_ids):",
        len(component_ids),
    )
    all_vul_ids = mysession.query(VulComponent.vulId).filter(VulComponent.component.in_(component_ids)).all()
    print(f"@@@@@@@@@ how many vulnerabilities were found for those components - {len(all_vul_ids)}")
    return [vul_id[0] for vul_id in all_vul_ids]


class VulnerabilityTestClass(Vulnerability):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Test 2: Get all the vulnerabilities from the Vulnerability table and compare them to the expected fixture
def test_vulnerabilities_by_ids(mysession, vul_ids):
    vulnerabilities = mysession.query(VulnerabilityTestClass).filter(VulnerabilityTestClass.id.in_(vul_ids)).all()

    # Make sure we have at least one vulnerability
    assert len(vulnerabilities) > 0

    # Create a list of vulnerability dictionaries
    vulnerabilities_list = [vuln.to_dict() for vuln in vulnerabilities]

    # # CREATING THE FIXTURES FILE, DONT DELETE
    # with open('vulnerabilities_list.json', 'w') as file:
    #     json.dump({"velnerability_fixtures": vulnerabilities_list}, file, default=str)

    # Relative path to the fixture file (relative to the current script)
    relative_path = "fixtures/vulnerabilities_list.json"
    data = getFixturesFromFile(relative_path)

    # Loop through the vulnerability_fixtures and compare each fixture to a vulnerability with the same id
    for fixture in data["velnerability_fixtures"]:
        vulnerability = next((v for v in vulnerabilities_list if v["id"] == fixture["id"]), None)

        assert vulnerability, f"No matching vulnerability found for fixture with id: {fixture['id']}"
        assert vulnerability["id"] == fixture["id"]
        assert vulnerability["publishedOn"] == fixture["publishedOn"]
        assert vulnerability["severity"] == fixture["severity"]
        assert vulnerability["cvssScore"] == fixture["cvssScore"]
        assert vulnerability["epssProbability"] == fixture["epssProbability"]
        assert vulnerability["txt"] == fixture["txt"]


def datetime_to_db_str(timestamp):
    tz_offset = timestamp.strftime("%z")
    tz_offset_formatted = f"{tz_offset[:3]}:{tz_offset[3:]}"
    return timestamp.strftime("%Y-%m-%d %H:%M:%S.%f ") + tz_offset_formatted


def getFixturesFromFile(relative_path):
    # Get the absolute path by joining the directory of the current script with the relative path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(script_dir, relative_path)

    with open(abs_path, "r") as file:
        data = json.load(file)
    return data
