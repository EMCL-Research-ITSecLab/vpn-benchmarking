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
                
        def run_with_rp(self, monitor):
            
            iterations = 0
            
            for path in os.listdir(dir_path):
                # check if current path is a file
                if os.path.isfile(os.path.join(dir_path, path)):
                    count += 1
                    
            print('File count:', count)
            for _ in range(iterations):
                pass
                
        def gen_keys(self, iterations):
            print(f"Generating {iterations} rosenpass and wireguard keys for server...")

            home_path = os.getcwd()
            os.makedirs(os.path.join(home_path, "rp-exchange/rp-keys"), exist_ok=True)

            for i in range(iterations):
                formatted_number = '{num:0>{len}}'.format(num=i + 1, len=len(str(iterations + 1)))
                os.system(f"rp genkey rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret")
                os.system(f"rp pubkey rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret rp-exchange/rp-keys/server-public/{formatted_number}_server.rosenpass-public")
                
        def count_rp_keys(self):
            exchange = HTTPExchange()
            return exchange.count_rp_keys()
                
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
                
        def count_rp_keys(self):
            exchange = HTTPExchange()
            return exchange.count_rp_keys()
        
                
    def count_rp_keys(self):
        path = os.path.join(os.getcwd(), "rp-exchange/rp-keys/")
        s_pub_path = os.path.join(path, "server-public")
        cl_pub_path = os.path.join(path, "client-public")
        
        s_pub_count, cl_pub_count = 0, 0
        for _ in os.listdir(s_pub_path):
            s_pub_count += 1
        for _ in os.listdir(cl_pub_path):
            cl_pub_count += 1
            
        # something went wrong if the number of keys in directories are unequal
        if s_pub_count != cl_pub_count:
            return -1
        
        # check if this is server or client by checking existence of secret keys
        try:
            key_path = os.path.join(path, "server-secret")
            
            count = 0
            for _ in os.listdir(key_path):
                count += 1
                
            if s_pub_count != count:
                return -1
        except:
            key_path = os.path.join(path, "client-secret")
            
            count = 0
            for _ in os.listdir(key_path):
                count += 1
                
            if s_pub_count != count:
                return -1
                            
        return s_pub_count


test_server = HTTPExchange.OnServer()

print(test_server.count_rp_keys())