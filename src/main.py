import logging
import os
import sys
import time
import docker
from services import *


def main():
    """MAIN"""
    client = docker.from_env()
    info = client.info()
    logging.info(f"Running Image-Swarm on {info.get('Name')}!")

    check_for_aws()
    if info.get("Swarm", {}).get("ControlAvailable", False):
        service_images = get_service_images()
    else:
        service_images = get_local_images()
    auth = get_auth_config()

    for image_name in service_images:
        logging.info(f"Checking for new image of: {image_name}")
        image = client.images.get(image_name)
        new = check_for_new_image(image, auth)

        if new:
            containers = client.containers.list(filters={"ancestor": f"{image_name}"})
            logging.info(f"Found {len(containers)} container with image {image_name}")

            for container in containers:
                logging.info(f"Killing {container.id}")
                container.kill()

    if os.environ.get("PRUNE", "true") == "true":
        logging.info("Pruning images")
        client.images.prune()

    sleep_length = os.environ.get("INTERVAL", 5 * 60)
    logging.info(f"Going to sleep for {sleep_length}s")
    time.sleep(int(sleep_length))


if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s",
                        level=getattr(logging, log_level))

    # Loop for a given number of times as specified in sys.argv[1] else forever
    run_loop = True
    counter = 1
    while run_loop:
        main()
        # Stop the loop if we are at the correct number of loops
        if len(sys.argv) > 2:
            if sys.arg[1] >= counter:
                run_loop = False
            counter += 1
