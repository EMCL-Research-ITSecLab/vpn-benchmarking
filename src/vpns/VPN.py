import os

import src.messages as messages
from src.HostsManager import HostsManager


class VPN:
    def __init__(self, role) -> None:
        self.home_path = os.getcwd()
        self.hosts = HostsManager()

        self.interface_name = None
        self.open_server_address = self.hosts.server_address

        if role not in ("server", "client"):
            messages.print_err(
                "Unable to open VPN connection: unknown role. Known: server, client"
            )
            raise Exception("Unknown role")
        else:
            self.role = role

    def open(self) -> bool:
        messages.print_err("VPN.open(self): NOT IMPLEMENTED")
        return False

    def close(self) -> bool:
        messages.print_err("VPN.close(self): NOT IMPLEMENTED")
        return False

    def generate_keys(self) -> bool:
        messages.print_err("VPN.generate_keys(self): NOT IMPLEMENTED")
        return False

    def share_pubkeys(self, remote_path) -> bool:
        messages.print_err("VPN.share_pubkeys(self, remote_path): NOT IMPLEMENTED")
        return False
