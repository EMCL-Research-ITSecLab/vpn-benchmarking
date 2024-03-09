import src.messages as messages

from HostsManager import HostsManager


class Server:
    """
    Bundles all the functions for the server. Calls the respective methods the server uses with the correct
    parameters. Allows running the actual exchanges as often as given as input through the given VPN and generating
    and sharing keys for the given VPN.
    """

    def __init__(self, exchange_type, vpn_type) -> None:
        """
        Loads the hosts addresses and creates instances of the given VPN and exchange classes with the correct
        parameters.
        :param exchange_type: Class to be used as Exchange type
        :param vpn_type: Class to be used as VPN type
        """
        messages.print_log("Initializing server...")

        self.hosts = HostsManager()
        if not self.hosts.load_from_file():
            return

        self.vpn = vpn_type(role="server")
        self.exchange = exchange_type(role="server", open_server_address="::", interface=self.vpn.interface_name)

        messages.print_log("Server initialized.")

    def run(self, number, monitor) -> bool:
        """
        Runs the exchange as often as given as input. Every exchange first opens the VPN, runs the exchange and
        closes the VPN. Does a manual poll before each step.
        :param number: number of exchanges to be executed
        :param monitor: monitor for handling the polls
        :return: True for success, False otherwise
        """
        for i in range(number):
            messages.print_log(f"Starting exchange {i + 1}...")

            # open the VPN
            monitor.poll("Server.run(): before opening VPN connection")
            if not self.vpn.open():
                return False

            # do one exchange
            monitor.poll("Server.run(): before doing next round of exchange")
            if not self.exchange.run():
                return False

            # close the VPN
            monitor.poll("Server.run(): before closing VPN connection")
            if not self.vpn.close():
                return False

        messages.print_log(f"Finished exchanges successfully.")
        return True

    def keygen(self) -> bool:  # only needed for VPN usage
        """
        Generates the necessary keys for the VPN. Only needed when a VPN is used, does nothing except for printing
        the messages in other case.
        :return: True for success, False otherwise
        """
        messages.print_log("Generating key set on the server...")

        if not self.vpn.generate_keys():
            return False

        messages.print_log("All needed keys are set up (none if no VPN is used).")
        return True

    def keysend(self, remote_path) -> bool:  # only needed for VPN usage
        """
        Sends the before generated public keys to the client's remote_path. Only needed when a VPN is used,
        does nothing except for printing the messages in other case.
        :param remote_path: working directory on the client, place keys into this directory
        :return: True for success, False otherwise
        """
        messages.print_log(
            "Transmitting public keys to the client (only if VPN is used)..."
        )

        if not self.vpn.share_pubkeys(remote_path):
            return False

        messages.print_log("Keys were successfully transmitted.")
        return True
