import logging
import os
from typing import List, Tuple, Union

import docker
import redis
from docker.client import DockerClient
from docker.errors import APIError
from docker.models.images import Image as DockerImage

from auth import get_redis_auth


def set_images(images: List[str]):
    """Set images in Redis"""

    host, port = get_redis_auth()
    store = redis.Redis(host=host, port=port)

    logging.info("Setting service images in Redis")
    for image in images:
        store.set(image, "true")


def get_images() -> List[str]:
    """Get images from Redis"""

    host, port = get_redis_auth()
    store = redis.Redis(host=host, port=port)

    logging.info("Getting service images from Redis")
    return [key.decode() for key in store.scan_iter()]


def get_local_images() -> List[str]:
    logging.info("List local images")

    client = docker.from_env()
    images = client.images.list()
    images = [tag
              for image in images
              for tag in image.tags]
    images = list(set(images))

    logging.info(f"Found {len(images)} images in swarm")
    return images


def get_service_images() -> List[str]:
    client = docker.from_env()
    services = client.services.list()

    if os.environ.get("FILTER_LABELS", "false") == "true":
        services = [service for service in services if
                    service.attrs.get("Spec", {}).get("Labels", {}).get("procedural.image-swarm.check",
                                                                        "false") == "true"]
    images = [service.attrs.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Image", None).split("@")[0] for
              service in services]
    images = list(set(images))

    logging.info(f"Found {len(images)} images in swarm")
    return images


def get_image_tags(image) -> Tuple[str, List[str]]:
    name, tag = image.tags[0].split(":")
    tags = [tag, ]

    if len(image.tags) > 1:
        return name, [_image.split(":")[1] for _image in image.tags]
    else:
        return name, tags


def pull_new_image(image: str, auth_config: dict, client: DockerClient):
    image_name, tag = image.split(":")
    logging.debug(f"Pulling tag: {tag}")

    _image = client.images.pull(image_name, tag=tag, auth_config=auth_config)
    logging.info(f"Pulled {_image.id}")
    return False


def check_for_new_image(image: Union[DockerImage, str], auth_config: dict):
    client = docker.from_env()
    if isinstance(image, str):
        logging.info(f"Pulling new image: {image}")
        return pull_new_image(image, auth_config, client)
    else:
        image_name, tags = get_image_tags(image)

    if "aws" not in image_name:
        logging.info("Removing Auth before pulling images")
        auth_config = {}

    try:
        registry_data = client.images.get_registry_data(image.tags[0], auth_config=auth_config)
    except APIError:
        logging.info(f"Could not find image: {image}. Skipping")
        return False

    if registry_data.id != get_repo_digest(image):
        logging.info(f"Pulling new version of {image}")

        for tag in tags:
            logging.debug(f"Pulling tag: {tag}")

            _image = client.images.pull(image_name, tag=tag, auth_config=auth_config)
            logging.info(f"Pulled {_image.id}")

        return True

    logging.info(f"Image: {image} is up to date")

    return False


def get_repo_digest(image: DockerImage) -> str:
    """Get the repo digest of an image"""

    repo_digests = image.attrs.get("RepoDigests", [])

    if len(repo_digests) == 0:
        return ""

    return repo_digests[0].split("@")[1]
