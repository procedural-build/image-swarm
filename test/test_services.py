import json
from pathlib import Path

import docker
from moto import mock_ecr
from services import get_service_images, check_for_new_image, get_auth_config


def test_get_service_images(mock_docker_api_client, create_service):

    images = get_service_images()

    assert images
    assert isinstance(images, list)
    assert images[0] == "busybox:latest"


def test_check_for_new_image(mock_docker_api_client):
    client = docker.from_env()
    image = client.images.get("busybox:latest")

    check_for_new_image(image, {"username": "test", "password": "test"})


@mock_ecr
def test_get_auth_config(aws_credentials, tmpdir):
    auth_config = get_auth_config(str(tmpdir))

    assert auth_config
    assert isinstance(auth_config, dict)
    assert auth_config.get("username")
    assert auth_config.get("password")


@mock_ecr
def test_get_auth_exist(aws_credentials, tmpdir):
    data = {"authorizationToken": "QVdTOjAxMjM0NTY3ODkxMC1hdXRoLXRva2Vu", "expiresAt": "2015-01-01T00:00:00+01:00", "proxyEndpoint": "https://012345678910.dkr.ecr.eu-west-2.amazonaws.com"}
    ecr_file = Path(str(tmpdir)) / "ecr.json"
    ecr_file.write_text(json.dumps(data))

    auth_config = get_auth_config(str(tmpdir))

    assert auth_config
    assert isinstance(auth_config, dict)
    assert auth_config.get("username")
    assert auth_config.get("password")
