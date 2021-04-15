import os
import time
import sys

from services import *
import logging


def main():
    """MAIN"""
    logging.info(f"Running Image-Swarm!")

    service_images = get_service_images()

    for service_image in service_images:
        new = check_for_new_image(service_image)
        if new:
            pull_new_image(service_image)
            container = find_local_container(service_image)
            if container:
                kill_container(container)

    sleep_length = os.environ.get("INTERVAL", 5 * 60)
    logging.info(f"Going to sleep for {sleep_length}s")
    time.sleep(sleep_length)


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
