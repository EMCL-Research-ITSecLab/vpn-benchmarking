from new_version.VPN import VPN
import messages
import new_version.helpers as helpers

import os


class Rosenpass(VPN):
    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        super().__init__(role, remote_ip_addr, remote_user)

    # TODO: Implement generate_keys
    # TODO: Implement count_keys

    def share_pubkeys(self, remote_path) -> bool:
        if self.role == "server":
            messages.print_log("Sending public keys to the client...")
        elif self.role == "client":
            messages.print_log("Sending public keys to the server... ")
        else:
            return False

        try:
            base_path = f"rp-keys/{self.role}-public/"
            for folder in os.listdir(base_path):
                success = helpers.send_file_to_host(
                    os.path.join(base_path, folder),
                    self.remote_user,
                    self.remote_ip_addr,
                    os.path.join(remote_path, base_path, folder),
                )
                if not success:
                    return False
        except:
            messages.print_err("Keys do not exist. Generate new keys with 'main.py'.")
            return False

        if self.role == "server":
            messages.print_log("Sent public keys to the client.")
        else:
            messages.print_log("Sent public keys to the server.")

        return True
