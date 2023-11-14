import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer


host_name = "localhost"
port = 8080

class HTTPExchange:
    class OnServer: 
        def run(self, reps, monitor):
            for _ in range(reps):
                monitor.poll()
                server = HTTPServer((host_name, port), HTTPExchange.OnServer.Server)
                server.handle_request()
                server.server_close()
                
        class Server(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()

    
    class OnClient:
        def run(self, reps, monitor):
            i = reps
            while i > 0:
                try:
                    monitor.poll()
                    connection = http.client.HTTPConnection(host_name, port, timeout=10)
                    connection.request("GET", "/")
                    # currently unused
                    response = connection.getresponse()
                    connection.close()
                    i -= 1
                # in case the server was not ready yet
                except:
                    continue
