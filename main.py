from http.server import BaseHTTPRequestHandler, HTTPServer
import os

from prometheus_client import start_http_server

from app.prometheus_collector import CollectorManager
from app.websitewebhook import start

DEFAULT_CONFIG_PATH = "/run/config/config.yaml"
DEFAULT_PORT = 8000
DEFAULT_METRICS_PORT = 8010


class app(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


if __name__ == "__main__":
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    CollectorManager.register_collectors()
    metrics_port = int(os.getenv('METRICS_PORT', DEFAULT_METRICS_PORT))
    start_http_server(int(metrics_port))

    config_path = os.getenv('CONFIG_PATH', DEFAULT_CONFIG_PATH)
    start(config_path)
    port = int(os.getenv('PORT', DEFAULT_PORT))
    logging.info(f"Starting server on port {port}")
    # setup readiness endpoint
    with HTTPServer(('', port), app) as server:
        server.serve_forever()
