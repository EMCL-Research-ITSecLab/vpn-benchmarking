import messages

import json
import time

hosts_path = "hosts.json"  # hosts file path, should not be changed


class Client:
    def __init__(self, ExchangeType, VPNType) -> None:
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
                    self.server_name = e["ip_addr"]
                    self.server_port = int(e["port"])
                    self.server_user = e["user"]
                    no_data = False
                elif e["role"] == "client":
                    self.client_ip_addr = e["ip_addr"]
                    self.client_user = e["user"]
                    no_data = False

            if no_data:
                raise Exception
        except:
            messages.print_err(
                "Data in 'hosts.json' is incorrect or empty. Repair the file using 'set_hosts.py'."
            )
            return

        messages.print_log("Client initialized.")

        self.exchange = ExchangeType(
            role="client", server_name=self.server_name, server_port=self.server_port
        )
        self.vpn = VPNType(
            role="client", remote_ip_addr=self.server_name, remote_user=self.server_user
        )

        return

    def run(self, number) -> bool:
        # TODO

        for i in range(number):
            messages.print_log(f"Starting exchange {i + 1}...")

            # open the VPN
            if not self.vpn.open():
                return False

            # do one exchange, try multiple times if necessary
            remaining_attempts = 50
            slept = False

            while True:
                if remaining_attempts > 0:  # still attempts left, normal case
                    if not self.exchange.run():
                        remaining_attempts -= 1
                    else:
                        break
                elif slept == False:  # if no more attempts but did not sleep yet
                    time.sleep(2)
                    remaining_attempts = 50
                    slept = True
                else:  # if no more attempts and already slept
                    messages.print_err(
                        "Too many exchange connection attempts. Did not finish successfully."
                    )
                    return False

            # close the VPN
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
