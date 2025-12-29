import os
import signal
import sys
import logging
from time import sleep

from app.websitewebhook import start_with_schedule, shutdown, execute_once

DEFAULT_CONFIG_PATH = "/run/config/config.yaml"


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logging.info(f"Received signal {signum}, shutting down gracefully...")
    shutdown()
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    config_path = os.getenv('CONFIG_PATH', DEFAULT_CONFIG_PATH)
    run_mode = os.getenv('RUN_MODE', 'daemon').lower()

    if run_mode == 'job':
        # Job mode: execute once and exit
        logging.info("Running in job mode - executing once and exiting")
        try:
            execute_once(config_path)
            logging.info("Job completed successfully")
        except Exception as ex:
            logging.error(f"Job failed with error: {ex}")
            sys.exit(1)  # Exit with error code to signal failure to Kubernetes
    else:
        # Daemon mode: continuous scheduling
        logging.info("Running in daemon mode - continuous scheduling")

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        start_with_schedule(config_path)
        
        # Keep the main thread alive
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt received, shutting down...")
            shutdown()
