import messages
import helpers

import os
import json

hosts_path = "hosts.json"  # hosts file path, should not be changed


class Server:
    def __init__(self) -> None:
        # open the hosts file
        messages.print_log("Initializing server...")
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

        messages.print_log("Server initialized.")
        return

    def run(self, ExchangeType, VPNType, number) -> bool:
        exchange = ExchangeType(
            role="server", server_name=self.server_name, server_port=self.server_port
        )
        vpn = VPNType(
            role="server",
            remote_ip_addr=self.client_ip_addr,
            remote_user=self.client_user,
        )

        for i in range(number):
            # open the VPN
            if not vpn.open():
                return False

            # do one exchange
            if not exchange.run():
                return False

            # close the VPN
            if not vpn.close():
                return False

        return True

    def prepare(self) -> bool:
        # TODO: Implement
        return False
