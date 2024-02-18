from helpers.vpns.VPN import VPN
import helpers.messages as messages
import helpers.helpers as helpers

import os
import subprocess
import click
import shutil
import time

key_path = "rp-keys"


class Rosenpass(VPN):
    keys_generated = False
    keys_shared = False

    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        super().__init__(role, remote_ip_addr, remote_user)

    def open(self) -> bool:
        # check if keys were generated and shared
        # possibly they were deleted -> then Rosenpass will throw an error
        if not (self.keys_generated and self.keys_shared):
            messages.print_err(
                "Keys are not correctly initialized. Try generating new keys and send them to the other host."
            )
            return False

        # FOR SERVER:
        self.process = self.__start_rosenpass_key_exchange_on_server()
        time.sleep(5)

        return False

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

        self.keys_generated = True
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

        self.keys_shared = True
        if self.role == "server":
            messages.print_log("Sent public keys to the client.")
        else:
            messages.print_log("Sent public keys to the server.")

        return True

    def __start_rosenpass_key_exchange_on_server(self):
        server_sk_dir = os.path.join(key_path, "server.rosenpass-secret")
        client_pk_dir = os.path.join(key_path, "client.rosenpass-public")
    
        try:
            process = subprocess.check_output(
                [
                    "sudo",
                    "rp",
                    "exchange",
                    server_sk_dir,  # server keys
                    "dev",
                    "rosenpass0",
                    "listen",
                    "localhost:9999",
                    "peer",
                    client_pk_dir,  # client keys
                    "allowed-ips",
                    "fe80::/64",
                ],
            )
        except Exception as err:
            messages.print_err("Rosenpass key exchange was not successful!")
            print(f"{err=}")
            return
        
        return process
