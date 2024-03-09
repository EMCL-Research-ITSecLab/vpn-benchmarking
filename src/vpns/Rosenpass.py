import os
import shutil
import signal
import subprocess

import click

import src.helpers as helpers
import src.messages as messages
from src.vpns.VPN import VPN

key_path = "rp-keys"
opening_port = 9999


class Rosenpass(VPN):
    """
    Implements the post-quantum secure Rosenpass VPN, that uses Wireguard.
    """
    process = None

    def __init__(self, role) -> None:
        """
        Calls VPNs __init__. Additionally, sets the Rosenpass interface name to 'rosenpass0' and the address of the
        server to 'fe80::1'.
        :param role: role of the host
        """
        super().__init__(role)
        self.interface_name = "rosenpass0"
        self.open_server_address = "[fe80::1]"

    def open(self) -> bool:
        """
        Opens the Rosenpass VPN. Will stay open after completion. Can be closed with the close method.
        :return: True for success, False otherwise
        """
        messages.print_log("Preparing...")
        self.__clean_up()  # close existing Rosenpass processes

        messages.print_log("Starting key exchange processes...")
        if self.role == "server":
            self.process = self.__start_rosenpass_key_exchange_on_server()
        elif self.role == "client":
            self.process = self.__start_rosenpass_key_exchange_on_client()
        else:
            raise Exception("Unexpected role")

        if not self.process:  # Process was not opened correctly
            return False

        # add an ip address to the interface
        if not self.__assign_ip_addr_to_interface():
            self.__clean_up()
            return False

        messages.print_log("Rosenpass connection established.")
        return True

    def close(self) -> bool:
        """
        Closes the Rosenpass VPN after cleanup.
        :return: True for success
        """
        self.__clean_up()
        messages.print_log("Rosenpass connection closed.")
        return True

    def generate_keys(self) -> bool:
        """
        Generates the necessary keys for Rosenpass. Creates or uses existing rp-keys directory,
        creates [role].rosenpass-secret and [role].rosenpass-public directories for Wireguard and Rosenpass secret
        and public keys. If key directories already exist, asks for overwriting, otherwise keeps existing keys.
        :return: True for success, False otherwise
        """
        messages.print_log(
            f"Generating Rosenpass and Wireguard key set for {self.role}..."
        )

        # Create directory if not existent
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

        # If key directories exist, ask for overwriting, otherwise keep old keys.
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

            messages.print_log(f"Generated keys for the {self.role}.")
            return True
        except Exception as err:
            messages.print_err(
                "Unable to generate keys: Perhaps Rosenpass is not installed or the key set already exists."
            )
            print(f"{err=}")
            return False

    def share_pubkeys(self, remote_path) -> bool:
        """
        Sends the before generated public Wireguard and Rosenpass keys to the other host. Will use the rp-keys/...
        directories on the remote host's remote_path. Key directories on the other host must exist.
        :param remote_path: path in which the rp-keys directory exists on the remote host
        :return: True for success, False otherwise
        """
        if self.role == "server":
            messages.print_log("Sending public keys to the client...")
            remote_user = self.hosts.client_user
            remote_address = self.hosts.client_address
        elif self.role == "client":
            messages.print_log("Sending public keys to the server... ")
            remote_user = self.hosts.server_user
            remote_address = self.hosts.server_address
        else:
            return False

        try:
            file_name = f"{self.role}.rosenpass-public"
            success = helpers.send_file_to_host(
                os.path.join(key_path, file_name),
                remote_user,
                remote_address,
                os.path.join(remote_path, key_path, file_name),
            )
            if not success:
                return False
        except Exception as err:
            messages.print_err("Keys do not exist. Generate new keys with 'main.py'.")
            print(f"{err=}")
            return False

        if self.role == "server":
            messages.print_log("Sent public keys to the client.")
        else:
            messages.print_log("Sent public keys to the server.")

        return True

    def __start_rosenpass_key_exchange_on_server(self):
        """
        Executes the command for starting the server key exchange.
        :return: True for success, False otherwise
        """
        messages.print_log("Starting process for Rosenpass key exchange...")

        server_sk_dir = os.path.join(key_path, "server.rosenpass-secret")
        client_pk_dir = os.path.join(key_path, "client.rosenpass-public")

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
                    opening_port,
                    "peer",
                    client_pk_dir,  # client keys
                    "allowed-ips",
                    "fe80::/64",
                ],
                stdout=subprocess.PIPE,
            )
        except Exception as err:
            messages.print_err("Rosenpass key exchange was not successful!")
            print(f"{err=}")
            self.__clean_up()
            return None

        messages.print_log("Rosenpass key exchange successfully started.")
        return process

    def __start_rosenpass_key_exchange_on_client(self):
        """
        Executes the command for starting the client key exchange.
        :return: True for success, False otherwise
        """
        messages.print_log("Starting process for Rosenpass key exchange...")

        client_sk_dir = os.path.join(key_path, "client.rosenpass-secret")
        server_pk_dir = os.path.join(key_path, "server.rosenpass-public")

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
                    f"{self.hosts.server_address}:{opening_port}",
                    "allowed-ips",
                    "fe80::/64",
                ],
                stdout=subprocess.PIPE,
            )
        except Exception as err:
            messages.print_err("Rosenpass key exchange was not successful!")
            print(f"{err=}")
            self.__clean_up()
            return None

        messages.print_log("Rosenpass key exchange successfully started.")
        return process

    def __assign_ip_addr_to_interface(self) -> bool:
        """
        Assigns the IP address 'fe80::1' to the server or 'fe80::2' to the client interface. Interface has to exist.
        Attempts multiple times, since the interface might not be ready for the first few tries. Flushes the
        interface after invalid attempt.
        :return: True for success, False otherwise
        """
        messages.print_log("Assigning IP address to rosenpass0...")

        if self.role == "server":
            number = 1  # fe80::1
        elif self.role == "client":
            number = 2  # fe80::2
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
                # flushes the interface for the case in which 'RTNETLINK answers: File exists error' occurs
                subprocess.run(
                    ["sudo", "ip", "addr", "flush", "dev", "rosenpass0"],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
                j -= 1
            except Exception as err:
                print(f"{err=}")
                return False

        # if adding an IP address failed
        if j == 0:
            messages.print_err(
                f"Too many attempts assigning IP address! Please try again."
            )
            return False

        messages.print_log("IP address assigned.")
        return True

    def __clean_up(self):
        """
        Terminates all running Rosenpass processes.
        """
        if self.process:
            self.process.kill()

        messages.print_log("Terminating all running Rosenpass processes...")

        try:
            for line in os.popen("ps ax | grep rosenpass | grep -v grep"):
                fields = line.split()
                if "main.py" not in line:
                    pid = fields[0]
                    os.kill(int(pid), signal.SIGKILL)
            messages.print_log("Rosenpass processes terminated.")
        except:  # no Rosenpass processes running
            messages.print_log("Nothing to terminate.")
