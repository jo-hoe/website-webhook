import os
import signal
import sys
import logging

from app.websitewebhook import start_with_schedule, shutdown, execute_once, simulate_once

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
        logging.info("Running in job mode - executing once and exiting")
        try:
            execute_once(config_path)
            logging.info("Job completed successfully")
        except Exception as ex:
            logging.error(f"Job failed with error: {ex}")
            sys.exit(1)

    elif run_mode == 'simulate':
        preset_value = os.getenv('PRESET_VALUE')
        logging.info(f"Running in simulate mode (preset='{preset_value}')")
        try:
            simulate_once(config_path, preset_value)
            logging.info("Simulate completed successfully")
        except Exception as ex:
            logging.error(f"Simulate failed: {ex}")
            sys.exit(1)

    else:
        logging.info("Running in daemon mode - continuous scheduling")

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        thread = start_with_schedule(config_path)
        thread.join()
