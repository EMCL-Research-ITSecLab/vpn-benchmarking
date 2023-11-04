from Monitoring import Monitoring

from http.server import BaseHTTPRequestHandler, HTTPServer


host_name = "localhost"
port = 8080


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()


def run_test(reps):
    for _ in range(reps):
        server = HTTPServer((host_name, port), Server)
        # server.handle_request()
        server.server_close()
        continue


if __name__ == "__main__":        
    monitor = Monitoring()
    monitor.run(run_test(1500))