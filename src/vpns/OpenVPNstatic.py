import os
import shutil
import signal
import subprocess

import click

import src.helpers as helpers
import src.messages as messages
from src.vpns.VPN import VPN

key_path = "openvpnstatic-keys"
opening_port = 1194


class OpenVPNstatic(VPN):
    """
    Implements the OpenVPN proof-of-concept version.
    """
    process = None

    def __init__(self, role) -> None:
        """
        Calls VPNs __init__. Additionally, sets the OpenVPN interface name to 'tun0' and the address of the
        server to '10.8.0.1'.
        :param role: role of the host
        """
        super().__init__(role)
        self.interface_name = "tun0"
        self.open_server_address = "10.8.0.1"

    def open(self) -> bool:
        """
        Opens the OpenVPN VPN. Will stay open after completion. Can be closed with the close method.
        :return: True for success, False otherwise
        """
        messages.print_log("Preparing...")
        self.__clean_up()  # close existing OpenVPN processes

        messages.print_log("Starting key exchange processes...")
        if self.role == "server":
            self.process = self.__start_openvpn_key_exchange_on_server()
        elif self.role == "client":
            self.process = self.__start_openvpn_key_exchange_on_client()
        else:
            raise Exception("Unexpected role")

        if not self.process:  # Process was not opened correctly
            return False

        # add an ip address to the interface
        if not self.__assign_ip_addr_to_interface():
            self.__clean_up()
            return False

        messages.print_log("OpenVPN connection established.")
        return True

    def close(self) -> bool:
        """
        Closes OpenVPN after cleanup.
        :return: True for success
        """
        self.__clean_up()
        messages.print_log("OpenVPN connection closed.")
        return True

    def generate_keys(self) -> bool:
        """
        Generates the necessary static key for OpenVPN. Creates or uses existing openvpnstatic-keys directory,
        creates openvpn-key. If key directories already exist, asks for overwriting, otherwise keeps existing keys.
        :return: True for success, False otherwise
        """
        messages.print_log(
            f"Generating OpenVPN static key for {self.role}..."
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

        k_path = f"{key_path}/openvpn.key"

        # If key directories exist, ask for overwriting, otherwise keep old keys.
        if os.path.exists(k_path):
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
                    "openvpn",
                    "--genkey",
                    "secret",
                    k_path,
                ],
                stderr=subprocess.PIPE,
            )

            messages.print_log(f"Generated keys for the {self.role}.")
            return True
        except Exception as err:
            messages.print_err(
                "Unable to generate keys: Perhaps OpenVPN is not installed or the key set already exists."
            )
            print(f"{err=}")
            return False

    def share_pubkeys(self, remote_path) -> bool:
        """
        Sends the before generated static OpenVPN key to the other host. Will use the openvpnstatic 
        directorie on the remote host's remote_path. Key directorie on the other host must exist.
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
            file_name = "openvpn.key"
            success = helpers.send_file_to_host(
                os.path.join(key_path, file_name),
                remote_user,
                remote_address,
                os.path.join(remote_path, key_path),
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

    def __start_openvpn_key_exchange_on_server(self):
        """
        Executes the command for starting the server key exchange.
        :return: True for success, False otherwise
        """
        messages.print_log("Starting OpenVPN key exchange...")

        key_dir = os.path.join(key_path, "openvpn.key")
        conf_dir = os.path.join(key_path, "openvpn.conf")

        try:
            subprocess.run( # Create openvpn.conf
                    f'echo "dev tun\nifconfig 10.8.0.1 10.8.0.2\nsecret {key_dir}\ncipher AES-256-CBC" > {conf_dir}',
                    shell=True,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
            process = subprocess.Popen(
               ["sudo", "openvpn", "--config", f"{conf_dir}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as err:
            messages.print_err("OpenVPN key exchange was not successful!")
            print(f"{err=}")
            self.__clean_up()
            return None
        

        return process

    def __start_openvpn_key_exchange_on_client(self):
        """
        Executes the command for starting the client key exchange.
        :return: True for success, False otherwise
        """
        messages.print_log("Starting OpenVPN key exchange...")

        key_dir = os.path.join(key_path, "openvpn.key")
        conf_dir = os.path.join(key_path, "openvpn.conf")

        try:
            subprocess.run( # Create openvpn.conf
                    f'echo "remote {self.hosts.server_address}\ndev tun\nifconfig 10.8.0.2 10.8.0.1\nsecret {key_dir}\ncipher AES-256-CBC" > {conf_dir}',
                    shell=True,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
            process = subprocess.Popen(
                ["sudo", "openvpn", "--config", f"{conf_dir}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as err:
            messages.print_err("OpenVPN key exchange was not successful!")
            print(f"{err=}")
            self.__clean_up()
            return None

        return process

    def __assign_ip_addr_to_interface(self) -> bool:
        """
        Assigns the IP address '10.8.0.1' to the server or '10.8.0.2' to the client interface. Interface has to exist.
        Attempts multiple times, since the interface might not be ready for the first few tries. Flushes the
        interface after invalid attempt.
        :return: True for success, False otherwise
        """

        if self.role == "server":
            number = 1  # 10.8.0.1
        elif self.role == "client":
            number = 2  # 10.8.0.2
        else:
            return False

        j = 1000  # number of attempts
        
        while j > 0:
            try:
                subprocess.check_output(
                    [
                        "sudo",
                        "ip",
                        "addr",
                        "add",
                        f"10.8.0.{number}/32",
                        "dev",
                        "tun0",
                    ],
                    stderr=subprocess.PIPE,
                )
                break
            except subprocess.CalledProcessError:
                # flushes the interface for the case in which 'RTNETLINK answers: File exists error' occurs
                subprocess.run(
                    ["sudo", "ip", "addr", "flush", "dev", "tun0"],
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
        
        try:
            # Add openvpn to route table
            subprocess.run(
                ["sudo", "ip", "route", "add", "10.8.0.0/24", "dev", "tun0"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except: # OpenVPN was already added to the route table
            pass


        return True

    def __clean_up(self):
        """
        Terminates all running OpenVPN processes.
        """
        if self.process:
            self.process.kill()

        try:
            for line in os.popen("ps ax | grep openvpn | grep -v grep"):
                fields = line.split()
                if "main.py" not in line:
                    pid = fields[0]
                    os.kill(int(pid), signal.SIGKILL)
        except Exception as err:  # no OpenVPN processes running
            return
