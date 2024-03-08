import time

import src.messages as messages
from src.HostsManager import HostsManager


class Client:
    def __init__(self, ExchangeType, VPNType) -> None:
        # open the hosts file
        messages.print_log("Initializing client...")

        self.hosts = HostsManager()

        messages.print_log("Client initialized.")

        self.vpn = VPNType(role="client")
        self.exchange = ExchangeType(
            role="client", open_server_address=self.vpn.open_server_address, interface=self.vpn.interface_name
        )

        return

    def run(self, number, monitor) -> bool:
        for i in range(number):
            messages.print_log(f"Starting exchange {i + 1}...")

            # open the VPN
            monitor.poll("Client.run(): before opening VPN connection")
            if not self.vpn.open():
                return False

            # do one exchange, try multiple times if necessary
            monitor.poll("Client.run(): before doing next round of exchange")
            remaining_attempts = 50
            slept = False

            while True:
                if remaining_attempts > 0:  # still attempts left, normal case
                    if not self.exchange.run():
                        remaining_attempts -= 1
                    else:
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
        messages.print_log("Generating key set on the client...")

        if not self.vpn.generate_keys():
            return False

        messages.print_log("All needed keys are set up (none if no VPN is used).")
        return True

    def keysend(self, remote_path) -> bool:  # only needed for VPN usage
        messages.print_log(
            "Transmitting public keys to the server (only if VPN is used)..."
        )

        if not self.vpn.share_pubkeys(remote_path):
            return False

        messages.print_log("Keys were successfully transmitted.")
        return True
