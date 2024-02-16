from new_version.VPN import VPN
import messages
import new_version.helpers as helpers

import os
import subprocess


class Rosenpass(VPN):
    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        super().__init__(role, remote_ip_addr, remote_user)

    def generate_keys(self) -> bool:
        messages.print_log(
            f"Generating Rosenpass and Wireguard key set for {self.role}..."
        )

        if not self.__create_key_directories():
            return False

        try:
            subprocess.check_output(
                [
                    "rp",
                    "genkey",
                    f"rp-keys/{self.role}-secret/{self.role}.rosenpass-secret",
                ],
            )
            subprocess.check_output(
                [
                    "rp",
                    "pubkey",
                    f"rp-keys/{self.role}-secret/{self.role}.rosenpass-secret",
                    f"rp-keys/{self.role}-public/{self.role}.rosenpass-public",
                ],
            )
        except Exception as err:
            messages.print_err(
                "Unable to generate keys: Perhaps Rosenpass is not installed or the key set already exists."
            )
            print(f"{err=}")
            return False

        messages.print_log(f"Generated keys for the {self.role}.")

        return True

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

    # TODO: Change so that only one folder with the correct number of keys exists
    def __count_keys(self) -> int:
        key_path = os.path.join(self.home_path, "rp-keys")
        server_pk_path = os.path.join(key_path, "server-public")
        client_pk_path = os.path.join(key_path, "client-public")

        server_pk_count, client_pk_count = 0, 0

        try:
            for _ in os.listdir(server_pk_path):
                server_pk_count += 1
        except:
            messages.print_err(
                "The folder rp-keys/server-public could not be found/opened. Generate and share new keys to proceed."
            )
            return -1
        try:
            for _ in os.listdir(client_pk_path):
                client_pk_count += 1
        except:
            messages.print_err(
                "The folder rp-keys/client-public could not be found/opened. Generate and share new keys to proceed."
            )
            return -1

        # something went wrong if the number of keys in directories are unequal
        if server_pk_count != client_pk_count:
            return -1

        sk_path = os.path.join(key_path, f"{self.role}-secret")

        count = 0
        try:
            for _ in os.listdir(sk_path):
                count += 1
        except:
            messages.print_err("Couldn't list key directory files.")
            return -1

        if server_pk_count != count:
            return -1

        return count

    def __create_key_directories(self) -> bool:
        messages.print_log("  Creating key directories...")

        try:
            # create secret key directory
            os.makedirs(
                os.path.join(self.home_path, f"rp-keys/{self.role}-secret"),
                exist_ok=True,
            )

            # create public key directory
            os.makedirs(
                os.path.join(self.home_path, f"rp-keys/{self.role}-public"),
                exist_ok=True,
            )
        except:
            messages.print_err("Unable to create key directories.")
            return False

        messages.print_log("  Created key directories.")
        return True
