from moto import mock_ecr
import os
from main import main


@mock_ecr
def test_main(mock_docker_api_client, aws_credentials, create_service):
    os.environ["INTERVAL"] = "0"
    main()
