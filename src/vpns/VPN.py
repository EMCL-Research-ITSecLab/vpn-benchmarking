import os

import src.messages as messages
from src.HostsManager import HostsManager


class VPN:
    """
    Base class for VPNs. To add a new VPN type, a class must inherit from VPN.
    """

    def __init__(self, role) -> None:
        """
        Loads all values needed for using the VPN, including current working directory and host addresses. Sets base
        interface name to None and address for opening to the server's public address. Checks if the role is valid,
        throws an Exception otherwise.
        :param role: role of the host, server or client
        """
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

    def open(self):
        """
        Opens the VPN with the set parameters. Implementation is done in inheriting classes.
        :return: False since not implemented
        """
        messages.print_err("VPN.open(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def close(self):
        """
        Closes the VPN. Implementation is done in inheriting classes.
        :return: False since not implemented
        """
        messages.print_err("VPN.close(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def generate_keys(self):
        """
        Generates the keys needed for a VPN exchange. Implementation is done in inheriting classes.
        :return: False since not implemented
        """
        messages.print_err("VPN.generate_keys(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def share_pubkeys(self, remote_path):
        """
        Sends the before generated public keys to the other host's remote_path.
        :param remote_path: working directory on the remote host, place keys into this directory
        :return: False since not implemented
        """
        messages.print_err("VPN.share_pubkeys(self, remote_path): NOT IMPLEMENTED")
        raise NotImplementedError
