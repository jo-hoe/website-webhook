from http.server import BaseHTTPRequestHandler, HTTPServer
import os

from app.websitewebhook import start


class app(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


if __name__ == "__main__":
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    start()

    # setup readiness endpoint
    with HTTPServer(('', os.getenv('PORT', 8080)), app) as server:
        server.serve_forever()
