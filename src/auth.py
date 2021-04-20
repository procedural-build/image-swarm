import base64
import datetime
import json
import logging
import os
from pathlib import Path
from typing import Tuple


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

        key_path = Path("/run/secrets/AWS_ACCESS_KEY_ID")
        secret_path = Path("/run/secrets/AWS_SECRET_ACCESS_KEY")

        if key_path.exists() and secret_path.exists():
            logging.debug(f"Reading AWS from secrets")

            os.environ["AWS_ACCESS_KEY_ID"] = key_path.read_text().strip()
            os.environ["AWS_SECRET_ACCESS_KEY"] = secret_path.read_text().strip()
        else:
            raise AttributeError("Could not find AWS environment variables")
    else:
        logging.debug("Found AWS in env var")


def check_for_redis():
    if not os.environ.get("REDIS_HOST") and not os.environ.get("REDIS_PORT"):

        host_path = Path("/run/secrets/REDIS_HOST")
        port_path = Path("/run/secrets/REDIS_PORT")

        if host_path.exists() and port_path.exists():
            logging.debug(f"Reading Redis from secrets")

            os.environ["REDIS_HOST"] = host_path.read_text().strip()
            os.environ["REDIS_PORT"] = port_path.read_text().strip()
        else:
            raise AttributeError("Could not find Redis environment variables")
    else:
        logging.debug("Found Redis in env var")


def get_redis_auth() -> Tuple[str, int]:
    host = os.environ.get("REDIS_HOST", "redis")
    port = int(os.environ.get("REDIS_PORT", 6379))

    return host, port
