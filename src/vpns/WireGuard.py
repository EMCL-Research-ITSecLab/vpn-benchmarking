import os
import shutil
import signal
import subprocess

import click

import src.helpers as helpers
import src.messages as messages
from src.vpns.VPN import VPN

key_path = "wg-keys"
opening_port = 51820


class WireGuard(VPN):
    """
    Implements the WireGuard VPN.
    """
    process = None

    def __init__(self, role) -> None:
        """
        Calls VPNs __init__. Additionally, sets the WireGuard interface name to 'wg0' and the address of the
        server to '10.0.0.1'.
        :param role: role of the host
        """
        super().__init__(role)
        self.interface_name = "wg0"
        self.open_server_address = "10.0.0.1"

    def open(self) -> bool:
        """
        Opens the WireGuard VPN. Will stay open after completion. Can be closed with the close method.
        :return: True for success, False otherwise
        """
        messages.print_log("Preparing...")
        self.__clean_up()  # close existing WireGuard processes

        try: # Delete old WiregGuard interface and create a new Wireguard interface
            subprocess.run(
                ["sudo","ip", "link", "del", "wg0"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["sudo","ip", "link", "add", "wg0", "type", "wireguard"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except: # Old interfaces does not exist: Create WireGuard interface
            subprocess.run(
                ["sudo","ip", "link", "add", "wg0", "type", "wireguard"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        messages.print_log("Starting key exchange processes...")
        if self.role == "server":
            self.process = self.__start_wg_key_exchange_on_server()
        elif self.role == "client":
            self.process = self.__start_wg_key_exchange_on_client()
        else:
            raise Exception("Unexpected role")

        if not self.process:  # Process was not opened correctly
            return False

        # add an ip address to the interface
        if not self.__assign_ip_addr_to_interface():
            self.__clean_up()
            return False

        messages.print_log("WireGuard connection established.")
        return True

    def close(self) -> bool:
        """
        Closes the WireGuard VPN after cleanup.
        :return: True for success
        """
        self.__clean_up()
        messages.print_log("WireGuard connection closed.")
        return True

    def generate_keys(self) -> bool:
        """
        Generates the necessary keys for WireGuard. Creates or uses existing wg-keys directory,
        creates [role].wg-secret and [role].wg-public directories for Wireguard and WireGuard secret.
        If key directories already exist, asks for overwriting, otherwise keeps existing keys.
        :return: True for success, False otherwise
        """
        messages.print_log(
            f"Generating Wireguard key set for {self.role}..."
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

        sk_path = f"{key_path}/{self.role}.wg-secret"
        pk_path = f"{key_path}/{self.role}.wg-public"

        # If key directories exist, ask for overwriting, otherwise keep old keys.
        if os.path.exists(sk_path) or os.path.exists(pk_path):
            messages.print_warn(
                "The folders for the keys already exist (and possibly the keys)."
            )
            if click.confirm("Overwrite existing key folders and generate new keys?"):
                shutil.rmtree(key_path, ignore_errors=False, onerror=None)
                os.mkdir(key_path)
            else:
                return True

        # Generate keys for WireGuard
        try:
            subprocess.check_output(
                """
                    "wg",
                    "genkey",
                    "|",
                    "tee",
                    sk_path,
                    "|",
                    "wg",
                    "pubkey",
                    ">",
                    pk_path
                ],
                stderr=subprocess.PIPE,
                """
                f"wg genkey | tee {sk_path} | wg pubkey > {pk_path}",
                shell=True, # use of shell for pipes "|" and redirections ">".
                stderr=subprocess.PIPE,    
            )
            messages.print_log(f"Generated keys for the {self.role}.")
            return True
        except Exception as err:
            messages.print_err(
                "Unable to generate keys: Perhaps WireGuard is not installed or the key set already exists."
            )
            print(f"{err=}")
            return False

    def share_pubkeys(self, remote_path) -> bool:
        """
        Sends the before generated public Wireguard key to the other host. Will use the wg-keys/...
        directories on the remote host's remote_path. Key directories on the other host must exist.
        :param remote_path: path in which the wg-keys directory exists on the remote host
        :return: True for success, False otherwise
        """
        if self.role == "server":
            messages.print_log("Sending public key to the client...")
            remote_user = self.hosts.client_user
            remote_address = self.hosts.client_address
        elif self.role == "client":
            messages.print_log("Sending public key to the server... ")
            remote_user = self.hosts.server_user
            remote_address = self.hosts.server_address
        else:
            return False

        try:
            file_name = f"{self.role}.wg-public"
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

    def __start_wg_key_exchange_on_server(self):
        """
        Executes the command for starting the server key exchange.
        :return: True for success, False otherwise
        """
        messages.print_log("Starting WireGuard key exchange...")

        server_sk_dir = os.path.join(key_path, "server.wg-secret")
        client_pk_dir = os.path.join(key_path, "client.wg-public")
        client_pk = open(client_pk_dir).readline().strip() # Contains the wg-public-key, strip() to remove whitespaces

        try: # Set WireGuard configuration and start key exchange
            process = subprocess.Popen(
                [
                    "sudo",
                    "wg",
                    "set",
                    "wg0",
                    "listen-port",
                    f"{opening_port}",
                    "private-key",
                    f"{server_sk_dir}",
                    "peer",
                    f"{client_pk}",                      
                    "allowed-ips",
                    "10.0.0.2/32",
                    "endpoint",
                    f"{self.hosts.client_address}:{opening_port}",    
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
    
        except Exception as err:
            messages.print_err("WireGuard key exchange was not successful!")
            print(f"{err=}")
            self.__clean_up()
            return None

        return process

    def __start_wg_key_exchange_on_client(self):
        """
        Executes the command for starting the client key exchange.
        :return: True for success, False otherwise
        """
        messages.print_log("Starting WireGuard key exchange...")

        client_sk_dir = os.path.join(key_path, "client.wg-secret")
        server_pk_dir = os.path.join(key_path, "server.wg-public")
        server_pk = open(server_pk_dir).readline().strip() # Contains the wg-public-key

        try: # Set WireGuard configuration and start key exchange
            process = subprocess.Popen(
                [
                    "sudo",
                    "wg",
                    "set",
                    "wg0",
                    "listen-port",
                    f"{opening_port}",
                    "private-key",
                    client_sk_dir,  # client secret key
                    "peer",
                    server_pk,  # server public key
                    "allowed-ips",
                    "10.0.0.1/32",
                    "endpoint",
                    f"{self.hosts.server_address}:{opening_port}",    
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        except Exception as err:
            messages.print_err("WireGuard key exchange was not successful!")
            print(f"{err=}")
            self.__clean_up()
            return None

        return process

    def __assign_ip_addr_to_interface(self) -> bool:
        """
        Assigns the IP address 'fe80::1' to the server or 'fe80::2' to the client interface. Interface has to exist.
        Attempts multiple times, since the interface might not be ready for the first few tries. Flushes the
        interface after invalid attempt.
        :return: True for success, False otherwise
        """

        if self.role == "server":
            number = 1  # 10.0.0.1
        elif self.role == "client":
            number = 2  # 10.0.0.2
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
                        f"10.0.0.{number}/32",
                        "dev",
                        "wg0",
                    ],
                    stderr=subprocess.PIPE,
                )
                break
            except subprocess.CalledProcessError:
                # flushes the interface for the case in which 'RTNETLINK answers: File exists error' occurs
                subprocess.run(
                    ["sudo", "ip", "addr", "flush", "dev", "wg0"],
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
        

        # Bring up the interface
        subprocess.run(
            ["sudo", "ip", "link", "set", "wg0", "up"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        try:
            # Add WireGuard to route table
            subprocess.run(
                ["sudo", "ip", "route", "add", "10.0.0.0/24", "dev", "wg0"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except: # Wirguard was already added to the route table
            pass
            

        return True

    def __clean_up(self):
        """
        Terminates all running WireGuard processes.
        """
        if self.process:
            self.process.kill()

        try:
            for line in os.popen("ps ax | grep wireguard | grep -v grep"):
                fields = line.split()
                if "main.py" not in line:
                    pid = fields[0]
                    os.kill(int(pid), signal.SIGKILL)
        except Exception as err:  # no WireGuard processes running
            return
