from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess
import pycurl
from messages import print_err, print_warn
import json

hosts_path = "hosts.json"  # path and for the hosts file, should not be changed


class HTTPExchange:
    class OnServer:
        def __init__(self) -> None:
            self.host_name = "NOT_IMPLEMENTED"
            self.port = 0

        def run(self, reps, monitor):
            for _ in range(reps):
                monitor.poll("onServer: before creating server")
                server = HTTPServer(
                    (self.host_name, self.port), HTTPExchange.OnServer.Server
                )
                server.handle_request()
                server.server_close()

        def run_with_rp(self, iterations, monitor):
            # check if the number of keys is consistent
            keys = self.__count_rp_keys()
            use_iterations = True

            if keys <= -1:
                print_err(
                    f"Number of keys in directories is not consistent. Generate new keys to proceed."
                )
                return
            elif keys == 0:
                print_err("No keys found. Generate new keys to proceed.")
                return
            elif keys == 1:
                if iterations == None:
                    iterations = 1
                elif iterations < 1:
                    print_err(
                        "Number of iterations was invalid. Please enter at least one iteration or generate new keys."
                    )
                    return
            else:
                print("Number of iterations was set to number of different keys.")
                iterations = keys
                use_iterations = False

            # enter sudo so it does not ask during the next commands
            subprocess.run(["sudo", "echo"], stdout=subprocess.PIPE)

            # only used for use_iterations == True, needed to avoid unbound variables
            server_key_path = os.path.join(
                os.getcwd(),
                f"rp-keys/server-secret/server.rosenpass-secret",
            )
            client_key_path = os.path.join(
                os.getcwd(),
                f"rp-keys/client-public/client.rosenpass-public",
            )

            for i in range(iterations):
                if not use_iterations:
                    print("starting iteration", i, "with key", i + 1)
                    formatted_number = "{num:0>{len}}".format(
                        num=i + 1, len=len(str(iterations + 1))
                    )
                    server_key_path = os.path.join(
                        os.getcwd(),
                        f"rp-keys/server-secret/{formatted_number}_server.rosenpass-secret",
                    )
                    client_key_path = os.path.join(
                        os.getcwd(),
                        f"rp-keys/client-public/{formatted_number}_client.rosenpass-public",
                    )
                else:
                    print("starting iteration", i)

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
                    except subprocess.CalledProcessError as e:
                        # RTNETLINK answers: File exists error
                        if "exit status 2" in str(e):
                            subprocess.run(
                                ["sudo", "ip", "addr", "flush", "dev", "rosenpass0"]
                            )
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
                if use_iterations:
                    print("ending iteration", i)
                else:
                    print("ending iteration", i, "with key", i + 1)

        def gen_keys(self, iterations):
            pass

        def send_public_keys_to_client(self, remote_path):
            pass

        def __count_rp_keys(self):
            pass

        class Server(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()

    class OnClient:
        def __init__(self) -> None:
            self.host_name = "NOT_IMPLEMENTED"
            self.port = 0

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

        def run_with_rp(self, iterations, monitor):
            # check if the number of keys is consistent
            keys = self.__count_rp_keys()
            use_iterations = True

            if keys == -1:
                print_err(
                    "Number of keys in directories is not consistent. Generate new keys to proceed."
                )
                return
            elif keys == 0:
                print_err("No keys found. Generate new keys to proceed.")
                return
            elif keys == 1:
                if iterations == None:
                    iterations = 1
                elif iterations < 1:
                    print_err(
                        "Number of iterations was invalid. Please enter at least one iteration or generate new keys."
                    )
                    return
            else:
                print("Number of iterations was set to number of different keys.")
                iterations = keys
                use_iterations = False

            subprocess.run(
                ["sudo", "echo"], stdout=subprocess.PIPE
            )  # enter sudo so it does not ask during the next commands

            # only used for use_iterations == True, needed to avoid unbound variables
            client_key_path = os.path.join(
                os.getcwd(),
                f"rp-keys/client-secret/client.rosenpass-secret",
            )
            server_key_path = os.path.join(
                os.getcwd(),
                f"rp-keys/server-public/server.rosenpass-public",
            )

            for i in range(iterations):
                if not use_iterations:
                    print("starting iteration", i, "with key", i + 1)
                    formatted_number = "{num:0>{len}}".format(
                        num=i + 1, len=len(str(iterations + 1))
                    )
                    client_key_path = os.path.join(
                        os.getcwd(),
                        f"rp-keys/client-secret/{formatted_number}_client.rosenpass-secret",
                    )
                    server_key_path = os.path.join(
                        os.getcwd(),
                        f"rp-keys/server-public/{formatted_number}_server.rosenpass-public",
                    )
                else:
                    print("starting iteration", i)

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
                    except subprocess.CalledProcessError as e:
                        # RTNETLINK answers: File exists error
                        if "exit status 2" in str(e):
                            subprocess.run(
                                ["sudo", "ip", "addr", "flush", "dev", "rosenpass0"]
                            )
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
                if use_iterations:
                    print("ending iteration", i)
                else:
                    print("ending iteration", i, "with key", i + 1)

        def gen_keys(self, iterations):
            pass

        def send_public_keys_to_server(self, remote_path):
            pass

        def __count_rp_keys(self):
            pass

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
        pass

    def send_file_to_host(self, file, target_user, target_ip_addr, target_path):
        pass

    # TODO: Add function to delete old keys
