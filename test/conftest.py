import pytest
import docker
import mockerpy
import mockerpy.services
import os


@pytest.fixture()
def mock_docker_api_client(monkeypatch, tmpdir):
    def mock():
        """
        Returns a Client with a fake APIClient.
        """
        client = docker.DockerClient(version="19.03.12")
        client.api = mockerpy.make_fake_api_client(tmpdir, None)
        return client

    monkeypatch.setattr(docker, "from_env", mock)


@pytest.fixture()
def create_service(tmpdir):
    mockerpy.services.create_fake_service(tmpdir, "test")


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'