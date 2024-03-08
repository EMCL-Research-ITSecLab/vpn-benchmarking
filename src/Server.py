import src.messages as messages

from src.HostsManager import HostsManager


class Server:
    def __init__(self, ExchangeType, VPNType) -> None:
        # open the hosts file
        messages.print_log("Initializing server...")

        self.hosts = HostsManager()

        messages.print_log("Server initialized.")

        self.vpn = VPNType(role="server")
        self.exchange = ExchangeType(role="server", open_server_address="::", interface=self.vpn.interface_name)

    def run(self, number, monitor) -> bool:
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
        messages.print_log("Generating key set on the server...")

        if not self.vpn.generate_keys():
            return False

        messages.print_log("All needed keys are set up (none if no VPN is used).")
        return True

    def keysend(self, remote_path) -> bool:  # only needed for VPN usage
        messages.print_log(
            "Transmitting public keys to the client (only if VPN is used)..."
        )

        if not self.vpn.share_pubkeys(remote_path):
            return False

        messages.print_log("Keys were successfully transmitted.")
        return True
