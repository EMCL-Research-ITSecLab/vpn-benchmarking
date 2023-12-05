from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess
import pycurl
from error_messages import print_err, print_warn
import json


class HTTPExchange:
    class OnServer:
        def __init__(self) -> None:
            try:
                file = open("data/hosts.json", "r")
                hosts = json.load(file)
                for e in hosts["hosts"]:
                    if e["role"] == "server":
                        self.host_name = e["ip_addr"]
                        self.port = int(e["port"])
            except:
                print_err(
                    'File "hosts.json" does not exist. Create the file using set_hosts.py.'
                )
                return

        def run(self, reps, monitor):
            for _ in range(reps):
                monitor.poll("onServer: before creating server")
                server = HTTPServer(
                    (self.host_name, self.port), HTTPExchange.OnServer.Server
                )
                server.handle_request()
                server.server_close()

        def run_with_rp(self, monitor):
            # check if the number of keys is consistent
            iterations = self.__count_rp_keys()

            if iterations == -1:
                print_err(
                    "Number of keys in directories is not consistent. Generate new keys to proceed."
                )
                return

            # enter sudo so it does not ask during the next commands
            subprocess.run(["sudo", "echo"], stdout=subprocess.PIPE)

            for i in range(iterations):
                print("starting iteration", i, "with key", i + 1)
                formatted_number = "{num:0>{len}}".format(
                    num=i + 1, len=len(str(iterations + 1))
                )
                server_key_path = os.path.join(
                    os.getcwd(),
                    f"rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret",
                )
                client_key_path = os.path.join(
                    os.getcwd(),
                    f"rp-exchange/rp-keys/client-public/{formatted_number}_client.rosenpass-public",
                )
                proc = subprocess.Popen(
                    [
                        "sudo",
                        "rp",
                        "exchange",
                        server_key_path,
                        "dev",
                        "rosenpass0",
                        "listen",
                        f"{self.host_name}:{self.port}",
                        "peer",
                        client_key_path,
                        "allowed-ips",
                        "fe80::/64",
                    ],
                    stdout=subprocess.PIPE,
                )

                # try to add an ip address
                j = 1000  # number of attempts
                while j > 0:
                    try:
                        subprocess.check_output(
                            [
                                "sudo",
                                "ip",
                                "a",
                                "add",
                                "fe80::1/64",
                                "dev",
                                "rosenpass0",
                            ],
                            stderr=subprocess.PIPE,
                        )
                        break
                    except:
                        j -= 1

                # if adding an ip address failed
                if j == 0:
                    print_err(
                        f"Too many attempts for key exchange {i + 1}! Please try again."
                    )
                    proc.kill()
                    return

                print(f"exchange {i} is ready...")

                # else
                self.run(1, monitor)
                proc.kill()
                print("ending iteration", i, "with key", i + 1)

        def gen_keys(self, iterations):
            if iterations < 2:
                # TODO: Implement for one key
                return

            print(
                f"Generating {iterations} rosenpass and wireguard keys for server... ",
                end="",
                flush=True,
            )

            home_path = os.getcwd()
            os.makedirs(os.path.join(home_path, "rp-exchange/rp-keys"), exist_ok=True)

            for i in range(iterations):
                formatted_number = "{num:0>{len}}".format(
                    num=i + 1, len=len(str(iterations + 1))
                )
                os.system(
                    f"rp genkey rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret"
                )
                os.system(
                    f"rp pubkey rp-exchange/rp-keys/server-secret/{formatted_number}_server.rosenpass-secret rp-exchange/rp-keys/server-public/{formatted_number}_server.rosenpass-public"
                )

            print("done.")

        # TODO: Add function to send the keys via ssh
        def send_public_keys_to_host(self, remote_path):
            # with open("data/hosts.json", "r") as file:
            #     json.load()
            
            # exchange = HTTPExchange()
            # exchange.send_file_to_host("rp-exchange/rp-keys/server-public", )
            pass

        def __count_rp_keys(self):
            exchange = HTTPExchange()
            return exchange.count_rp_keys()

        class Server(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()

    class OnClient:
        def __init__(self) -> None:
            try:
                file = open("data/hosts.json", "r")
                hosts = json.load(file)
                for e in hosts["hosts"]:
                    if e["role"] == "server":
                        self.host_name = e["ip_addr"]
                        self.port = int(e["port"])
            except:
                print_err(
                    'File "hosts.json" does not exist. Create the file using set_hosts.py.'
                )
                return

        def run(self, reps, monitor):
            i = reps
            while i > 0:
                try:
                    monitor.poll("onClient: before connecting")
                    self.__http_get(f"http://{self.host_name}:{self.port}")
                    i -= 1
                # in case the server was not ready yet
                except:
                    continue

        # when having errors try "sudo ip addr flush dev rosenpass0"

        def run_with_rp(self, monitor):
            # check if the number of keys is consistent
            iterations = self.__count_rp_keys()

            if iterations == -1:
                print_err(
                    "Number of keys in directories is not consistent. Generate new keys to proceed."
                )
                return

            subprocess.run(
                ["sudo", "echo"], stdout=subprocess.PIPE
            )  # enter sudo so it does not ask during the next commands

            for i in range(iterations):
                print("starting iteration", i, "with key", i + 1)
                formatted_number = "{num:0>{len}}".format(
                    num=i + 1, len=len(str(iterations + 1))
                )
                client_key_path = os.path.join(
                    os.getcwd(),
                    f"rp-exchange/rp-keys/client-secret/{formatted_number}_client.rosenpass-secret",
                )
                server_key_path = os.path.join(
                    os.getcwd(),
                    f"rp-exchange/rp-keys/server-public/{formatted_number}_server.rosenpass-public",
                )
                proc = subprocess.Popen(
                    [
                        "sudo",
                        "rp",
                        "exchange",
                        client_key_path,
                        "dev",
                        "rosenpass0",
                        "peer",
                        server_key_path,
                        "endpoint",
                        f"{self.host_name}:{self.port}",
                        "allowed-ips",
                        "fe80::/64",
                    ],
                    stdout=subprocess.PIPE,
                )

                # try to add an ip address
                j = 1000  # number of attempts
                while j > 0:
                    try:
                        subprocess.check_output(
                            [
                                "sudo",
                                "ip",
                                "a",
                                "add",
                                "fe80::2/64",
                                "dev",
                                "rosenpass0",
                            ],
                            stderr=subprocess.PIPE,
                        )
                        break
                    except:
                        j -= 1

                # if adding an ip address failed
                if j == 0:
                    print_err(
                        f"Too many attempts for key exchange {i + 1}! Please try again."
                    )
                    proc.kill()
                    return

                print(f"exchange {i} is ready...")

                # else
                self.run(1, monitor)
                proc.kill()
                print("ending iteration", i, "with key", i + 1)

        def gen_keys(self, iterations):
            print(
                f"Generating {iterations} rosenpass and wireguard keys for client... ",
                end="",
                flush=True,
            )

            home_path = os.getcwd()
            os.makedirs(os.path.join(home_path, "rp-exchange/rp-keys"), exist_ok=True)

            for i in range(iterations):
                formatted_number = "{num:0>{len}}".format(
                    num=i + 1, len=len(str(iterations + 1))
                )
                subprocess.run(
                    [
                        "rp",
                        "genkey",
                        f"rp-exchange/rp-keys/client-secret/{formatted_number}_client.rosenpass-secret",
                    ]
                )
                subprocess.run(
                    [
                        "rp",
                        "pubkey",
                        f"rp-exchange/rp-keys/client-secret/{formatted_number}_client.rosenpass-secret",
                        f"rp-exchange/rp-keys/client-public/{formatted_number}_client.rosenpass-public",
                    ]
                )

            print("done.")

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

    def send_file_to_host(self, file, user, receiver, target_path):
        try:
            subprocess.check_output(
                ["scp", file, f"{user}@{receiver}:{target_path}"],
                stderr=subprocess.PIPE,
            )
        except:
            print_err(
                "SSH connection to send files could not be established. Check if the needed SSH keys are set up."
            )
