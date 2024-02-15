import messages

import json

hosts_path = "hosts.json"  # hosts file path, should not be changed


class Server:
    setup_completed = False
    
    def __init__(self, ExchangeType, VPNType) -> None:
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

        self.exchange = ExchangeType(
            role="server", server_name=self.server_name, server_port=self.server_port
        )
        self.vpn = VPNType(
            role="server",
            remote_ip_addr=self.client_ip_addr,
            remote_user=self.client_user,
        )

        return

    def run(self, number) -> bool:
        if not self.setup_completed:
            messages.print_err("The setup has not been completed yet. Run the setup first.")
            return False
        
        for i in range(number):
            messages.print_log(f"Starting exchange {i+1}...")

            # open the VPN
            if not self.vpn.open():
                return False

            # do one exchange
            if not self.exchange.run():
                return False

            # close the VPN
            if not self.vpn.close():
                return False

        messages.print_log(f"Finished exchanges successfully.")
        return True

    def setup(self, remote_path) -> bool:
        messages.print_log("Generating key set on the server...")

        if not self.vpn.generate_keys():
            return False

        messages.print_log("Generated keys.")
        messages.print_log("Transmitting public keys to the client...")

        if not self.vpn.share_pubkeys(remote_path):
            return False

        messages.print_log("Setup complete.")
        self.setup_completed = True
        return True
