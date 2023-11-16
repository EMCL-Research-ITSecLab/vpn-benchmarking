import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import time


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
                
        def gen_keys(self, iterations):
            print(f"Generating {iterations} rosenpass and wireguard keys for server...")

            home_path = os.getcwd()
            os.makedirs(os.path.join(home_path, "rp-exchange/rp-keys"), exist_ok=True)

            for i in range(iterations):
                formatted_number = '{num:0>{len}}'.format(num=i + 1, len=len(str(iterations + 1)))
                os.system(f"rp genkey rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret")
                os.system(f"rp pubkey rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret rp-exchange/rp-keys/server-public/{formatted_number}_server.rosenpass-public")
                
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
                
        def gen_keys(self, iterations):
            print(f"Generating {iterations} rosenpass and wireguard keys for client...")

            home_path = os.getcwd()
            os.makedirs(os.path.join(home_path, "rp-exchange/rp-keys"), exist_ok=True)

            for i in range(iterations):
                formatted_number = '{num:0>{len}}'.format(num=i + 1, len=len(str(iterations + 1)))
                os.system(f"rp genkey rp-exchange/rp-keys/client-secret/{formatted_number}_client.rosenpass-secret")
                os.system(f"rp pubkey rp-exchange/rp-keys/client-secret/{formatted_number}_client.rosenpass-secret rp-exchange/rp-keys/client-public/{formatted_number}_client.rosenpass-public")


test_server = HTTPExchange.OnServer()
test_client = HTTPExchange.OnClient()

start = time.time()
test_server.gen_keys(500)
end = time.time()
print(end - start)
# start = time.time()
# test_client.gen_keys(500)
# end = time.time()
# print(end - start)