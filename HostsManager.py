import json

from helpers import messages

hosts_path = "hosts.json"  # hosts file path, should not be changed


class HostsManager:
    server_address = None
    client_address = None
    server_user = None
    client_user = None

    def __init__(self):
        self.__load_from_file()

    def __load_from_file(self):
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
                    self.server_address = e["ip_addr"]
                    self.server_user = e["user"]
                    no_data = False
                elif e["role"] == "client":
                    self.client_address = e["ip_addr"]
                    self.client_user = e["user"]
                    no_data = False

            if no_data:
                raise Exception
        except:
            messages.print_err(
                "Data in 'hosts.json' is incorrect or empty. Repair the file using 'set_hosts.py'."
            )
            return
