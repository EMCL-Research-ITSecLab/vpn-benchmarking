from helpers.vpns.VPN import VPN
import helpers.messages as messages
import helpers.helpers as helpers

import os
import subprocess
import click
import shutil

key_path = "rp-keys"


class Rosenpass(VPN):
    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        super().__init__(role, remote_ip_addr, remote_user)

    def generate_keys(self) -> bool:
        messages.print_log(
            f"Generating Rosenpass and Wireguard key set for {self.role}..."
        )

        if not os.path.exists(key_path):
            try:
                os.mkdir(key_path)
            except Exception as err:
                messages.print_err(
                    "Something went wrong when creating the key directory."
                )
                print(f"{err=}")
                return False

        sk_path = f"{key_path}/{self.role}.rosenpass-secret"
        pk_path = f"{key_path}/{self.role}.rosenpass-public"

        if os.path.exists(sk_path) or os.path.exists(pk_path):
            messages.print_warn(
                "The folders for the keys already exist (and possibly the keys)."
            )
            if click.confirm("Overwrite existing key folders and generate new keys?"):
                shutil.rmtree(key_path, ignore_errors=False, onerror=None)
            else:
                return True

        try:
            subprocess.check_output(
                [
                    "rp",
                    "genkey",
                    sk_path,
                ],
            )
            subprocess.check_output(
                [
                    "rp",
                    "pubkey",
                    sk_path,
                    pk_path,
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
            file_name = f"{self.role}.rosenpass-public"
            success = helpers.send_file_to_host(
                os.path.join(key_path, file_name),
                self.remote_user,
                self.remote_ip_addr,
                os.path.join(remote_path, key_path, file_name),
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
