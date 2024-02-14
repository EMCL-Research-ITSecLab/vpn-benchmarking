from new_version.VPN import VPN
import messages
import helpers

import os


class Rosenpass(VPN):
    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        super().__init__(role, remote_ip_addr, remote_user)

    # TODO: TEST
    def share_pubkeys(self, remote_path) -> bool:
        if self.role == "server":
            messages.print_log("Sending public keys to the client...")

            try:
                base_path = "rp-keys/server-public/"
                for folder in os.listdir(base_path):
                    helpers.send_file_to_host(
                        os.path.join(base_path, folder),
                        self.remote_user,
                        self.remote_ip_addr,
                        os.path.join(remote_path, base_path, folder),
                    )
            except:
                messages.print_err(
                    "Keys do not exist. Generate new keys with 'main.py'."
                )
                return False

            messages.print_log("Sent public keys to the client.")
            return True
        elif self.role == "client":
            messages.print_log("Sending public keys to the server...")

            try:
                base_path = "rp-keys/client-public/"
                for folder in os.listdir(base_path):
                    helpers.send_file_to_host(
                        os.path.join(base_path, folder),
                        self.remote_user,
                        self.remote_ip_addr,
                        os.path.join(remote_path, base_path, folder),
                    )
            except:
                messages.print_err(
                    "Keys do not exist. Generate new keys with 'main.py'."
                )
                return False

            messages.print_log("Sent public keys to the server.")
            return True

        return False
