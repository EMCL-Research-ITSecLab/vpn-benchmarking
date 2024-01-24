import helpers
import messages
import json


hosts_path = "hosts.json"  # hosts file path, should not be changed


class HTTP:
    def start_server_and_handle_one_request(self):
        pass

    def stop_server(self):
        pass


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

    def run(self, type, vpn):
        pass


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
rosenpass = helpers.Rosenpass(role="server")
rosenpass.generate_keys(10)
