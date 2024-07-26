from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class app(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


if __name__ == "__main__":
    with HTTPServer(('', os.getenv('PORT', 8080)), app) as server:
        server.serve_forever()
