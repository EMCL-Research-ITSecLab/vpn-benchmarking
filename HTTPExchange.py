import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import os


host_name = "localhost"
port = 8080

class HTTPExchange:
    class OnServer: 
        def run(self, reps, monitor):
            for _ in range(reps):
                monitor.poll("onServer: before creating server")
                server = HTTPServer((host_name, port), HTTPExchange.OnServer.Server)
                server.handle_request()
                server.server_close()
                
        # def gen_keys(self, iterations):
        #     print(f"Generating {iterations} rosenpass and wireguard keys...")
        #     os.system("mkdir rp-exchange")
        #     os.system("mkdir rp-exchange/rp-server-keys")
        #     os.system("mkdir rp-exchange/rp-server-keys/tmp")
        #     os.system("cd rp-exchange/rp-server-keys/tmp")
        #     os.system("rp genkey server.rosenpass-secret")
            
        #     keys = { "keys": [] }
        #     for i in range(iterations):
        #         new_key = {
        #             "number": i,
        #             "key_file": 
        #         }
        #         keys["keys"].append(new_key)
                    
        #     with open(f"rp-exchange/all-rp-server-keys.json", "w") as all_keys:
        #         pass
                
        class Server(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()

    
    class OnClient:
        def run(self, reps, monitor):
            i = reps
            while i > 0:
                try:
                    monitor.poll("onClient: before connecting")
                    connection = http.client.HTTPConnection(host_name, port, timeout=10)
                    connection.request("GET", "/")
                    # currently unused
                    response = connection.getresponse()
                    connection.close()
                    i -= 1
                # in case the server was not ready yet
                except:
                    continue
