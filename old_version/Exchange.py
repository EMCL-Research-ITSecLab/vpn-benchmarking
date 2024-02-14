from email import message_from_binary_file
from http.server import BaseHTTPRequestHandler, HTTPServer

import old_version.helpers as helpers
import messages
import json
import os


hosts_path = "hosts.json"  # hosts file path, should not be changed


class HTTP:
    def __init__(self, host_name, port) -> None:
        self.host_name = host_name
        self.port = port

    def handle_requests_and_close(self, number):
        if number < 0:
            messages.print_err("Negative number of requests!")
            return

        for i in range(number):
            print(f"{i + 1}: ", end="", flush=True)
            server = HTTPServer((self.host_name, self.port), HTTP.Server)
            print("Awaiting request... ", end="", flush=True)
            server.handle_request()

            messages.print_log("Closing server.")
            server.server_close()

    class Server(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()


class Server:
    def __init__(self) -> None:
        # open the hosts file
        messages.print_log("Initializing server...")
        try:
            file = open(hosts_path, "r")
        except:
            messages.print_err(
                "File 'hosts.json' could not be opened. Create the file using 'set_hosts.py'."
            )
            return

        # load data and set server name and port
        try:
            hosts = json.load(file)
            no_data = True

            for e in hosts["hosts"]:
                if e["role"] == "server":
                    self.host_name = e["ip_addr"]
                    self.port = int(e["port"])
                    no_data = False

            if no_data:
                raise Exception
        except:
            messages.print_err(
                "Data in 'hosts.json' is incorrect or empty. Repair the file using 'set_hosts.py'."
            )
            return

        messages.print_log("Server initialized.")
        return

    def run(self, type, vpn, number):
        # check if vpn option is valid
        if vpn not in (None, "rosenpass"):
            messages.print_err("Unable to run: unknown VPN. Known: None, rosenpass")
            return

        if type not in ("http"):
            messages.print_err("Unable to run: unknown type of exchange. Known: http")
            return

        if number < 1:
            messages.print_err("Unable to run: negative number of repetitions.")
            return

        # run without vpn
        if vpn == None:
            if number == 1:
                messages.print_log("Starting exchange without VPN...")
            else:
                messages.print_log(f"Starting {number} exchanges without VPN...")

            if type == "http":
                http_handler = HTTP(self.host_name, self.port)
                http_handler.handle_requests_and_close(number)

            # implement new exchange types here

        # implement new vpn types here

        if number == 1:
            messages.print_log("Exchange finished.")

    def send_public_keys_to_client(self, remote_path):
        try:
            with open(hosts_path, "r") as file:
                hosts = json.load(file)
        except:
            messages.print_err(
                "File 'hosts.json' could not be opened. Create the file using 'set_hosts.py'."
            )
            return

        c_ip_addr, c_user = None, None

        var_set = False
        for e in hosts["hosts"]:
            if e["role"] == "client":
                c_ip_addr = e["ip_addr"]
                c_user = e["user"]
                var_set = True

        if var_set == False:
            messages.print_err(
                "'hosts.json' does not contain information about the client."
            )
            return

        messages.print_log("Sending public keys to the client... ")

        try:
            base_path = "rp-keys/server-public/"
            for folder in os.listdir(base_path):
                helpers.send_file_to_host(
                    os.path.join(base_path, folder),
                    c_user,
                    c_ip_addr,
                    os.path.join(remote_path, base_path, folder),
                )
        except:
            messages.print_err("Keys do not exist. Generate new keys with 'main.py'.")
            return

        messages.print_log("Sent public keys to the client.")


class Client:
    def __init__(self) -> None:
        # open the hosts file
        messages.print_log("Initializing client...")
        try:
            file = open(hosts_path, "r")
        except:
            messages.print_err(
                "File 'hosts.json' could not be opened. Create the file using 'set_hosts.py'."
            )
            return

        # load data and set server name and port
        try:
            hosts = json.load(file)
            no_data = True

            for e in hosts["hosts"]:
                if e["role"] == "server":
                    self.host_name = e["ip_addr"]
                    self.port = int(e["port"])
                    no_data = False

            if no_data:
                raise Exception
        except:
            messages.print_err(
                "Data in 'hosts.json' is incorrect or empty. Repair the file using 'set_hosts.py'."
            )
            return

        messages.print_log("Client initialized.")
        return

    def run(self, type, vpn):
        pass


# ONLY FOR TESTING PURPOSES
# rosenpass = helpers.Rosenpass(role="server")
# rosenpass.generate_keys(10)

# helpers.send_file_to_host("test", "test", "test", "test")
