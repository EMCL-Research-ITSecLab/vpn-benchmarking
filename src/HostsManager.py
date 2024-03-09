import json

from src import messages

hosts_path = "hosts.json"  # hosts file path, should not be changed


class HostsManager:
    """
    Manages the hosts information imported from the hosts file.
    """
    server_address = None  # IP address of the server
    client_address = None  # IP address of the client
    server_user = None  # username on the server
    client_user = None  # username on the client

    def __init__(self) -> None:
        """
        Loads the hosts information from the hosts file.
        """
        self.__load_from_file()

    def __load_from_file(self) -> bool:
        """
        Opens the hosts file and extracts the addresses and usernames of the server and client.
        :return: True for success, False otherwise
        """
        try:
            file = open(hosts_path, "r")
        except:
            messages.print_err(
                "File 'hosts.json' could not be opened. Create the file using 'set_hosts.py'."
            )
            return False

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
                raise ValueError

            return True
        except ValueError:
            messages.print_err(
                "Data in 'hosts.json' is incorrect or empty. Repair the file using 'set_hosts.py'."
            )
            return False
        except Exception as err:
            print(f"{err=}")
            return False
