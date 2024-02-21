from helpers.vpns.VPN import VPN
import helpers.messages as messages
import helpers.helpers as helpers

import os
import subprocess
import click
import shutil
import signal
import sys
import time

key_path = "rp-keys"


class Rosenpass(VPN):
    process = None

    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        super().__init__(role, remote_ip_addr, remote_user)

    def open(self) -> bool:
        messages.print_log("Preparing...")
        self.__clean_up()

        messages.print_log("Starting key exchange processes...")
        if self.role == "server":
            self.process = self.__start_rosenpass_key_exchange_on_server()
        elif self.role == "client":
            self.process = self.__start_rosenpass_key_exchange_on_client()
        else:
            messages.print_err("Something went wrong! Unexpected role.")
            return False

        if self.process == None:  # Something went wrong
            return False

        if not self.__assign_ip_addr_to_interface():
            self.__clean_up()
            return False

        messages.print_log("Rosenpass connection established.")
        return True

    def close(self) -> bool:
        self.__clean_up()
        messages.print_log("Rosenpass connection closed.")
        return True

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
        messages.print_log("  Starting process for Rosenpass key exchange...")

        server_sk_dir = os.path.join(key_path, "server.rosenpass-secret")
        client_pk_dir = os.path.join(key_path, "client.rosenpass-public")

        successful = True
        try:
            process = subprocess.Popen(
                [
                    "sudo",
                    "rp",
                    "exchange",
                    server_sk_dir,  # server keys
                    "dev",
                    "rosenpass0",
                    "listen",
                    "9999",
                    "peer",
                    client_pk_dir,  # client keys
                    "allowed-ips",
                    "fe80::/64",
                ],
            )
        except Exception:
            messages.print_err("  Rosenpass key exchange was not successful!")
            successful = False

        if successful:
            messages.print_log("  Rosenpass key exchange successfully started.")
            return process
        else:
            self.__clean_up()
            return None

    def __start_rosenpass_key_exchange_on_client(self):
        messages.print_log("  Starting process for Rosenpass key exchange...")

        client_sk_dir = os.path.join(key_path, "client.rosenpass-secret")
        server_pk_dir = os.path.join(key_path, "server.rosenpass-public")

        successful = True
        server_ip_addr = self.remote_ip_addr
        try:
            process = subprocess.Popen(
                [
                    "sudo",
                    "rp",
                    "exchange",
                    client_sk_dir,  # client keys
                    "dev",
                    "rosenpass0",
                    "peer",
                    server_pk_dir,  # server keys
                    "endpoint",
                    f"{server_ip_addr}:9999",
                    "allowed-ips",
                    "fe80::/64",
                ],
            )
        except Exception:
            messages.print_err("  Rosenpass key exchange was not successful!")
            successful = False

        if successful:
            messages.print_log("  Rosenpass key exchange successfully started.")
            return process
        else:
            self.__clean_up()
            return None

    def __assign_ip_addr_to_interface(self) -> bool:
        messages.print_log("  Assigning IP address to rosenpass0...")

        if self.role == "server":
            number = 1  # number in IP address
        elif self.role == "client":
            number = 2
        else:
            return False
        j = 1000  # number of attempts

        while j > 0:
            try:
                subprocess.check_output(
                    [
                        "sudo",
                        "ip",
                        "a",
                        "add",
                        f"fe80::{number}/64",
                        "dev",
                        "rosenpass0",
                    ],
                    stderr=subprocess.PIPE,
                )
                break
            except subprocess.CalledProcessError:
                # RTNETLINK answers: File exists error
                subprocess.Popen(
                    ["sudo", "ip", "addr", "flush", "dev", "rosenpass0"],
                    stderr=subprocess.PIPE,
                )
                j -= 1
            except Exception as err:
                print(f"{err=}")
                return False
        # if adding an ip address failed
        if j == 0:
            messages.print_err(
                f"  Too many attempts assigning IP address! Please try again."
            )
            return False

        messages.print_log("  IP address assigned.")
        return True

    def __clean_up(self):
        if self.process != None:
            self.process.kill()

        messages.print_log("  Terminating all running Rosenpass processes...")

        try:
            for line in os.popen("ps ax | grep rosenpass | grep -v grep"):
                fields = line.split()
                pid = fields[0]
                os.kill(int(pid), signal.SIGKILL)
            messages.print_log("  Rosenpass processes terminated.")
        except:
            messages.print_log("  Nothing to terminate.")
