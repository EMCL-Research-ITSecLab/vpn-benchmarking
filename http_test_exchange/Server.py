from http.server import BaseHTTPRequestHandler, HTTPServer


host_name = "localhost"
port = 8080


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()


def serve_once():
    server = HTTPServer((host_name, port), Server)
    server.handle_request()
    server.server_close()


if __name__ == "__main__":        
    for i in range(1000):
        serve_once()