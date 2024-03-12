import json
import os
from pathlib import Path

import click

from src import messages
from src.messages import print_warn, print_log

hosts_path = "hosts.json"  # hosts file path, should not be changed
ansible_path = "ansible_files"


class HostsManager:
    """
    Manages the host information. Either creates a new hosts file or loads the information from an existing file.
    """

    hosts = {"hosts": []}

    def __init__(self,
                 server_address=None,
                 client_address=None,
                 server_user=None,
                 client_user=None
                 ) -> None:
        """
        Either creates a file using the given arguments or loads the data from an existing file. Either all
        arguments have to be given or neither.
        :param server_address: IP address of the server
        :param client_address: IP address of the client
        :param server_user: username on the server
        :param client_user: username on the client
        """
        self.server_address = server_address
        self.client_address = client_address
        self.server_user = server_user
        self.client_user = client_user

        # if all arguments are given, create the file from these values
        if (
                server_address and client_address and server_user and client_user
        ):
            self.__create_file()
            return

        # if all arguments are None (or not given), load from file
        if not (
                server_address or client_address or server_user or client_user
        ):
            self.__load_from_file()
            return

        raise ValueError

    def __create_file(self) -> None:
        """
        Creates the hosts file using the stored information. Asks if an Ansible hosts file should also be created
        afterward and creates it if wanted.
        """

        server = {
            "role": "server",
            "ip_addr": self.server_address,
            "user": self.server_user,
        }
        client = {
            "role": "client",
            "ip_addr": self.client_address,
            "user": self.client_user,
        }

        self.hosts["hosts"].append(server)
        self.hosts["hosts"].append(client)

        if not self.__write_data():
            print_warn("Did not create a new hosts file.")
            return

        print_log(f"File {os.path.basename(hosts_path)} was created and filled.")

        if os.path.exists(os.path.join(ansible_path, "hosts")):
            if click.confirm(
                    "\nDerive ansible hosts file (this will overwrite the existing file)?"
            ):
                self.__derive_ansible_hosts(self.server_user, self.server_address, self.client_user,
                                            self.client_address)
        else:
            if click.confirm("\nDerive ansible hosts file?"):
                self.__derive_ansible_hosts(self.server_user, self.server_address, self.client_user,
                                            self.client_address)

    def __write_data(self) -> bool:
        """
        Writes data to a hosts file. If file already exists, asks for confirmation to overwrite it, otherwise stops.
        :return: True for success, False otherwise
        """
        if os.path.exists(hosts_path):
            print_warn('The file "hosts.json" already exists.')

            if not click.confirm("Overwrite existing file?"):
                return False
            os.remove(hosts_path)

        try:
            with open(hosts_path, "a") as file:
                json.dump(self.hosts, indent=2, fp=file)
            return True
        except Exception as err:
            print(f"{err=}")
            return False

    @staticmethod
    def __derive_ansible_hosts(s_user, s_ip_addr, c_user, c_ip_addr) -> None:
        """
        Derives an Ansible hosts file from the stored information.
        :param s_user: username of the server
        :param s_ip_addr: IP address of the server
        :param c_user: username of the client
        :param c_ip_addr: IP address of the client
        :return:
        """
        ansible_hosts_path = os.path.join(ansible_path, "hosts")
        if os.path.exists(ansible_hosts_path):
            os.remove(ansible_hosts_path)

        Path(ansible_path).mkdir(parents=True, exist_ok=True)
        with open(ansible_hosts_path, "a") as file:
            file.write("[senders]\n")
            file.write(f"server ansible_host={s_ip_addr} ansible_user={s_user}\n\n")
            file.write("[receivers]\n")
            file.write(f"client ansible_host={c_ip_addr} ansible_user={c_user}")

    def __load_from_file(self) -> bool:
        """
        Opens the hosts file and extracts the addresses and usernames of the server and client.
        :return: True for success, False otherwise
        """
        try:
            file = open(hosts_path, "r")
        except FileNotFoundError:
            messages.print_err(
                "File 'hosts.json' could not be opened. Create the file first."
            )
            return False
        except Exception as err:
            messages.print_err(
                "File 'hosts.json' could not be opened."
            )
            print(f"{err=}")
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
