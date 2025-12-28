from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import signal
import sys

from prometheus_client import start_http_server

from app.prometheus_collector import CollectorManager
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
    import logging
    logging.info(f"Received signal {signum}, shutting down gracefully...")
    shutdown()
    sys.exit(0)


if __name__ == "__main__":
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    config_path = os.getenv('CONFIG_PATH', DEFAULT_CONFIG_PATH)
    run_mode = os.getenv('RUN_MODE', 'daemon').lower()

    if run_mode == 'job':
        # Job mode: execute once and exit
        logging.info("Running in job mode - executing once and exiting")
        execute_once(config_path)
        logging.info("Job completed successfully")
    else:
        # Daemon mode: continuous scheduling with HTTP server
        logging.info("Running in daemon mode - continuous scheduling")

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        CollectorManager.register_collectors()
        metrics_port = int(os.getenv('METRICS_PORT', DEFAULT_METRICS_PORT))
        start_http_server(int(metrics_port))

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
