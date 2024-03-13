import time

import src.messages as messages
from src.HostsManager import HostsManager


class Client:
    """
    Bundles all the functions for the client. Calls the respective methods the client uses with the correct
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
        messages.print_log("Initializing client...")

        self.hosts = HostsManager()

        self.vpn = vpn_type(role="client")
        self.exchange = exchange_type(
            role="client", open_server_address=self.vpn.open_server_address, interface=self.vpn.interface_name
        )

        messages.print_log("Client initialized.")

    def run(self, number, monitor) -> bool:
        """
        Runs the exchange as often as given as input. Every exchange first opens the VPN, attempts to run the
        exchange multiple times and closes the VPN. Stops after too many unsuccessful exchange attempts. Does a
        manual poll before each step.
        :param number: number of exchanges to be executed
        :param monitor: monitor for handling the polls
        :return: True for success, False otherwise
        """
        i = 0
        while i < number:
            messages.print_log(f"Starting exchange {i + 1}...")

            # open the VPN
            monitor.poll("Client.run(): before opening VPN connection")
            if not self.vpn.open():
                return False

            # do one exchange, try multiple times if necessary
            monitor.poll("Client.run(): before doing next round of exchange")
            remaining_attempts = 50
            slept = False

            messages.print_log(f"Sending packet to {self.vpn.open_server_address}...")
            while True:
                if remaining_attempts > 0:  # still attempts left, normal case
                    return_code = self.exchange.run()
                    if return_code == 0:
                        i -= 1  # only go to next round when return_code is 0 (success)
                        break
                    elif return_code == 1:
                        remaining_attempts -= 1
                    else:  # error has occurred that requires starting VPN again
                        break
                elif not slept:  # if no more attempts but did not sleep yet
                    time.sleep(2)
                    remaining_attempts = 50
                    slept = True
                else:  # if no more attempts and already slept
                    messages.print_err(
                        "Too many exchange connection attempts. Did not finish successfully."
                    )
                    return False

            # close the VPN
            monitor.poll("Client.run(): before closing VPN connection")
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
        messages.print_log("Generating key set on the client...")

        if not self.vpn.generate_keys():
            return False

        messages.print_log("All needed keys are set up (none if no VPN is used).")
        return True

    def keysend(self, remote_path) -> bool:  # only needed for VPN usage
        """
        Sends the before generated public keys to the server's remote_path. Only needed when a VPN is used,
        does nothing except for printing the messages in other case.
        :param remote_path: working directory on the server, place keys into this directory
        :return: True for success, False otherwise
        """
        messages.print_log(
            "Transmitting public keys to the server (only if VPN is used)..."
        )

        if not self.vpn.share_pubkeys(remote_path):
            return False

        messages.print_log("Keys were successfully transmitted.")
        return True
