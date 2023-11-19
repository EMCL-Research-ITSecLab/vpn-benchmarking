import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process
import os
import time
import subprocess
import datetime
import pycurl


host_name = "localhost"
port = 8080

class HTTPExchange:
    class OnServer: 
        def run(self, reps, monitor):
            for _ in range(reps):
                # monitor.poll("onServer: before creating server")
                server = HTTPServer((host_name, port), HTTPExchange.OnServer.Server)
                server.handle_request()
                server.server_close()
                
        def run_with_rp(self, monitor):
            # check if the number of keys is consistent
            iterations = self.__count_rp_keys()
            
            if iterations == -1:
                print(f"[{datetime.datetime.now().isoformat()} ERROR] An error occurred. Number of keys in directories is not consistent. Generate new keys to proceed.")
                return
            
            subprocess.run(['sudo', 'echo'], stdout=subprocess.PIPE)    # enter sudo so it does not ask during the next commands

            for i in range(iterations):
                formatted_number = '{num:0>{len}}'.format(num=i + 1, len=len(str(iterations + 1)))
                server_key_path = os.path.join(os.getcwd(), f"rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret")
                client_key_path = os.path.join(os.getcwd(), f"rp-exchange/rp-keys/client-public/{formatted_number}_client.rosenpass-public")
                proc = subprocess.Popen(['sudo', 'rp', 'exchange', server_key_path, 'dev', 'rosenpass0', 'listen', 'localhost:9999', 'peer', client_key_path, 'allowed-ips', 'fe80::/64'], stdout=subprocess.PIPE)

                # try to add an ip address
                i = 10      # number of attempts
                while i > 0:
                    try:
                        subprocess.check_output(['sudo', 'ip', 'a', 'add', 'fe80::1/64', 'dev', 'rosenpass0'], stderr=subprocess.PIPE)
                        break
                    except:
                        i -= 1

                # if adding an ip address failed
                if i == 0:
                    print(f"[{datetime.datetime.now().isoformat()} ERROR] Too many attempts for key exchange {i + 1}! Please try again.")
                    proc.kill()
                    return

                # else
                time.sleep(10)
                proc.kill()
                            
        def gen_keys(self, iterations):
            print(f"Generating {iterations} rosenpass and wireguard keys for server...")

            home_path = os.getcwd()
            os.makedirs(os.path.join(home_path, "rp-exchange/rp-keys"), exist_ok=True)

            for i in range(iterations):
                formatted_number = '{num:0>{len}}'.format(num=i + 1, len=len(str(iterations + 1)))
                os.system(f"rp genkey rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret")
                os.system(f"rp pubkey rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret rp-exchange/rp-keys/server-public/{formatted_number}_server.rosenpass-public")
                
        # TODO: Add function to send the keys via ssh
                
        def __count_rp_keys(self):
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
                    # monitor.poll("onClient: before connecting")
                    self.__http_get(f"http://{host_name}:{port}")
                    i -= 1
                # in case the server was not ready yet
                except:
                    continue

        def run_with_rp(self, monitor):
            # check if the number of keys is consistent
            iterations = self.__count_rp_keys()
            
            if iterations == -1:
                print(f"[{datetime.datetime.now().isoformat()} ERROR] An error occurred. Number of keys in directories is not consistent. Generate new keys to proceed.")
                return
            
            subprocess.run(['sudo', 'echo'], stdout=subprocess.PIPE)    # enter sudo so it does not ask during the next commands

            # TODO: Change localhost to the servers actual ip address
            for i in range(iterations):
                formatted_number = '{num:0>{len}}'.format(num=i + 1, len=len(str(iterations + 1)))
                client_key_path = os.path.join(os.getcwd(), f"rp-exchange/rp-keys/client-secret/{formatted_number}_client.rosenpass-secret")
                server_key_path = os.path.join(os.getcwd(), f"rp-exchange/rp-keys/server-public/{formatted_number}_server.rosenpass-public")
                proc = subprocess.Popen(['sudo', 'rp', 'exchange', client_key_path, 'dev', 'rosenpass0', 'peer', server_key_path, 'endpoint', 'localhost:9999', 'allowed-ips', 'fe80::/64'], stdout=subprocess.PIPE)

                # try to add an ip address
                i = 10      # number of attempts
                while i > 0:
                    try:
                        subprocess.check_output(['sudo', 'ip', 'a', 'add', 'fe80::2/64', 'dev', 'rosenpass0'], stderr=subprocess.PIPE)
                        break
                    except:
                        i -= 1

                # if adding an ip address failed
                if i == 0:
                    print(f"[{datetime.datetime.now().isoformat()} ERROR] Too many attempts for key exchange {i + 1}! Please try again.")
                    proc.kill()
                    return

                # else
                time.sleep(2)
                proc.kill()
                
        def gen_keys(self, iterations):
            print(f"Generating {iterations} rosenpass and wireguard keys for client...")

            home_path = os.getcwd()
            os.makedirs(os.path.join(home_path, "rp-exchange/rp-keys"), exist_ok=True)

            for i in range(iterations):
                formatted_number = '{num:0>{len}}'.format(num=i + 1, len=len(str(iterations + 1)))
                os.system(f"rp genkey rp-exchange/rp-keys/client-secret/{formatted_number}_client.rosenpass-secret")
                os.system(f"rp pubkey rp-exchange/rp-keys/client-secret/{formatted_number}_client.rosenpass-secret rp-exchange/rp-keys/client-public/{formatted_number}_client.rosenpass-public")
                
        def __count_rp_keys(self):
            exchange = HTTPExchange()
            return exchange.count_rp_keys()
        
        def __http_get(self, url, iface=None):
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPGET, True)
            c.setopt(pycurl.TIMEOUT, 10)
            if iface:
                c.setopt(pycurl.INTERFACE, iface)
            c.perform()
            c.close()
                
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
