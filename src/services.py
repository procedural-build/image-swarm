import base64
import datetime
import json
import logging
import os
from pathlib import Path
from typing import List, Tuple

import docker
from docker.models.images import Image as DockerImage


def get_service_images() -> List[DockerImage]:
    client = docker.from_env()
    services = client.services.list()

    images = [service.attrs.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Image", None) for
              service in services]

    logging.info(f"Found {len(images)} images in swarm")
    return images


def get_image_tags(image) -> Tuple[str, List[str]]:
    name, tag = image.tags[0].split(":")
    tags = [tag, ]

    if len(image.tags) > 1:
        return name, [_image.split(":")[1] for _image in image.tags]
    else:
        return name, tags


def check_for_new_image(image: DockerImage, auth_config: dict):
    client = docker.from_env()
    image_name, tags = get_image_tags(image)

    registry_data = client.images.get_registry_data(image.tags[0], auth_config=auth_config)

    if registry_data.id != image.id:
        logging.info(f"Pulling new version of {image}")

        for tag in tags:
            logging.debug(f"Pulling tag: {tag}")

            client.images.pull(image_name, tag=tag, auth_config=auth_config)

        return True

    logging.info(f"Image: {image} is up to date")
    return False


def get_auth_config(path="/tmp"):
    logging.debug(f"Getting ECR auth")

    ecr_file = Path(path) / "ecr.json"
    if ecr_file.exists():
        logging.debug(f"Found ECR token locally")

        ecr_data = json.loads(ecr_file.read_text())
        token = ecr_data.get('authorizationToken')

        expire = datetime.datetime.fromisoformat(ecr_data.get("expiresAt"))
        if datetime.datetime.now(datetime.timezone(expire.utcoffset())) > expire + datetime.timedelta(minutes=15):
            token = _get_ecr_token(ecr_file)
    else:
        token = _get_ecr_token(ecr_file)

    token = base64.b64decode(token).decode()
    username, password = token.split(':')
    auth_config = {'username': username, 'password': password}

    return auth_config


def _get_ecr_token(ecr_file):
    import boto3

    logging.debug(f"Getting new ECR token")

    sess = boto3.Session()
    response = sess.client('ecr').get_authorization_token()
    auth_data = response['authorizationData'][0]
    auth_data.update({"expiresAt": auth_data.get("expiresAt").isoformat()})
    ecr_file.write_text(json.dumps(auth_data))

    return response['authorizationData'][0].get('authorizationToken')


def check_for_aws():
    if not os.environ.get("AWS_ACCESS_KEY_ID") and not os.environ.get("AWS_SECRET_ACCESS_KEY"):
        raise AttributeError("Could not find AWS environment variables")
