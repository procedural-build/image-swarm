import pytest
from moto import mock_ecr
import os
from main import main


@mock_ecr
@pytest.mark.skip()
def test_main(mock_docker_api_client, aws_credentials, create_service):
    os.environ["INTERVAL"] = "0"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_HOST"] = "redis"
    main()
