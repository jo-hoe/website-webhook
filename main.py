from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import signal
import sys
import logging

from app.websitewebhook import start_with_schedule, shutdown, execute_once

DEFAULT_CONFIG_PATH = "/run/config/config.yaml"
DEFAULT_PORT = 8000
DEFAULT_METRICS_PORT = 8010


class app(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


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
            sys.exit(1)  # Exit with error code to signal failure
    else:
        # Daemon mode: continuous scheduling with HTTP server
        logging.info("Running in daemon mode - continuous scheduling")

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        start_with_schedule(config_path)
        port = int(os.getenv('PORT', DEFAULT_PORT))
        logging.info(f"Starting server on port {port}")
        # setup readiness endpoint
        try:
            with HTTPServer(('', port), app) as server:
                server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt received, shutting down...")
            shutdown()
