from new_version.VPN import VPN
import messages
import new_version.helpers as helpers

import os
import subprocess


class Rosenpass(VPN):
    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        super().__init__(role, remote_ip_addr, remote_user)

    def generate_keys(self, number=1) -> bool:
        if number == 1:
            messages.print_log(
                f"Generating Rosenpass and Wireguard key set for {self.role}..."
            )

            self.__create_key_directories()

            try:
                subprocess.check_output(
                    [
                        "rp",
                        "genkey",
                        f"rp-keys/{self.role}-secret/{self.role}.rosenpass-secret",
                    ],
                    stderr=subprocess.PIPE,
                )
                subprocess.check_output(
                    [
                        "rp",
                        "pubkey",
                        f"rp-keys/{self.role}-secret/{self.role}.rosenpass-secret",
                        f"rp-keys/{self.role}-public/{self.role}.rosenpass-public",
                    ],
                    stderr=subprocess.PIPE,
                )
            except:
                messages.print_err(
                    "Unable to generate keys: Perhaps Rosenpass is not installed or the key set already exists."
                )
                return False
        elif number > 1:
            messages.print_log(
                f"Generating {number} Rosenpass and Wireguard key sets for {self.role}..."
            )

            try:
                os.makedirs(os.path.join(self.home_path, "rp-keys"), exist_ok=True)
            except:
                messages.print_err("Unable to create key directory.")
                return False

            for i in range(number):
                formatted_number = "{num:0>{len}}".format(
                    num=i + 1, len=len(str(number + 1))
                )

                self.__create_key_directories()

                try:
                    subprocess.check_output(
                        [
                            "rp",
                            "genkey",
                            f"rp-keys/{self.role}-secret/{formatted_number}_{self.role}.rosenpass-secret",
                        ],
                        stderr=subprocess.PIPE,
                    )
                    subprocess.check_output(
                        [
                            "rp",
                            "pubkey",
                            f"rp-keys/{self.role}-secret/{formatted_number}_{self.role}.rosenpass-secret",
                            f"rp-keys/{self.role}-public/{formatted_number}_{self.role}.rosenpass-public",
                        ],
                        stderr=subprocess.PIPE,
                    )
                except:
                    messages.print_err(
                        "Unable to generate keys: Perhaps Rosenpass is not installed or the key sets already exist."
                    )
                    return False
        else:
            messages.print_err("Number of iterations cannot be negative!")
            return False

        messages.print_log(f"Generated keys for the {self.role}.")

        return True

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

    def __create_key_directories(self) -> bool:
        messages.print_log("Creating key directories...")
        
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

        messages.print_log("Created key directories.")
        return True
