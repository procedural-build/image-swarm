from typing import List

import boto3
import docker
from docker.models.images import Image as DockerImage


def get_service_images() -> List[DockerImage]:
    client = docker.from_env()
    services = client.services.list()

    images = [service.attr.get("image") for service in services]
    return images


def check_for_new_image(service_image):
    repository_uri, tag = _tag.split(":")
    repository_name = repository_uri.split("/")[1]

    # Check against image available on the ECR registry
    aws_client = boto3.client('ecr')
    ecr_images = aws_client.list_images(
        registryId=REGISTRY_ID,
        repositoryName=repsitory_name,
        filter={"tagStatus": "TAGGED"}
    )

    # Re-map the image ids to get the id by tag
    digests_by_tag = {i['imageTag']: i['imageDigest'] for i in ecr_images['imageIds']}
    _id = digests_by_tag.get(tag, None)

    # Pull the image (if there is a difference)
    if _id and image.attrs["Id"] is not _id:
        docker_client.images.pull(repository_uri, tag=tag)


def pull_new_image(service_image):
    raise NotImplemented


def find_local_container(service_image):
    raise NotImplemented


def kill_container(container):
    raise NotImplemented
