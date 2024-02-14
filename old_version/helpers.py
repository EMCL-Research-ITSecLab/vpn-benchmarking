import messages
import os
import subprocess
import json
import old_version.helpers as helpers

hosts_path = "hosts.json"  # path and for the hosts file, should not be changed


class Rosenpass:
    def __init__(self, role) -> None:
        self.home_path = os.getcwd()

        if role not in ("server", "client"):
            messages.print_err("Unknown role as input.")
            self.role = None
            return

        self.role = role

    def generate_keys(self, iterations):
        if self.role not in ("server", "client"):
            messages.print_err("Unable to generate keys: no role.")
            return

        if iterations == 1:
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
                return
        elif iterations > 1:
            messages.print_log(
                f"Generating {iterations} Rosenpass and Wireguard key sets for {self.role}..."
            )

            try:
                os.makedirs(os.path.join(self.home_path, "rp-keys"), exist_ok=True)
            except:
                messages.print_err("Unable to create key directory.")
                return

            for i in range(iterations):
                formatted_number = "{num:0>{len}}".format(
                    num=i + 1, len=len(str(iterations + 1))
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
                    return
        else:
            messages.print_err("Number of iterations cannot be negative!")
            return

        messages.print_log(f"Generated keys for the {self.role}.")

    def count_keys(self):
        path = os.path.join(self.home_path, "rp-keys")
        s_pub_path = os.path.join(path, "server-public")
        cl_pub_path = os.path.join(path, "client-public")

        s_pub_count, cl_pub_count = 0, 0

        try:
            for _ in os.listdir(s_pub_path):
                s_pub_count += 1
        except:
            messages.print_err(
                "The folder rp-keys/server-public could not be found/opened. Generate and share new keys to proceed."
            )
            return -1
        try:
            for _ in os.listdir(cl_pub_path):
                cl_pub_count += 1
        except:
            messages.print_err(
                "The folder rp-keys/client-public could not be found/opened. Generate and share new keys to proceed."
            )
            return -1

        # something went wrong if the number of keys in directories are unequal
        if s_pub_count != cl_pub_count:
            return -1

        # check if this is server or client by checking existence of secret keys
        s_key_path = os.path.join(path, "server-secret")
        c_key_path = os.path.join(path, "client-secret")

        count = 0
        if os.path.exists(s_key_path):
            for _ in os.listdir(s_key_path):
                count += 1
        elif os.path.exists(c_key_path):
            for _ in os.listdir(c_key_path):
                count += 1
        else:
            messages.print_err("Key path was not found.")

        if s_pub_count != count:
            return -1

        return s_pub_count

    def share_public_keys(self, remote_path):
        if self.role not in ("server", "client"):
            messages.print_err("Unable to share keys: no role.")
            return

        try:
            with open(hosts_path, "r") as file:
                hosts = json.load(file)
        except:
            messages.print_err(
                "File 'hosts.json' could not be opened. Create the file using 'set_hosts.py'."
            )
            return

        ip_addr, user = None, None

        var_set = False
        for e in hosts["hosts"]:
            if e["role"] == self.role:
                ip_addr = e["ip_addr"]
                user = e["user"]
                var_set = True

        if var_set == False:
            messages.print_err(
                f"'hosts.json' does not contain information about the {self.role}."
            )
            return

        if self.role == "server":
            messages.print_log("Sending public keys to the client...")
        else:
            messages.print_log("Sending public keys to the server... ")

        try:
            base_path = f"rp-keys/{self.role}-public/"
            for folder in os.listdir(base_path):
                helpers.send_file_to_host(
                    os.path.join(base_path, folder),
                    user,
                    ip_addr,
                    os.path.join(remote_path, base_path, folder),
                )
        except:
            messages.print_err("Keys do not exist. Generate new keys with 'main.py'.")
            return

        messages.print_log(f"Sent public keys to the other host.")

    def __create_key_directories(self):
        if self.role not in ("server", "client"):
            messages.print_err("Unable to create key directories: false or no role.")
            return -1

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
            return -1

        return 0


def send_file_to_host(file, target_user, target_ip_addr, target_path):
    try:
        subprocess.check_output(
            ["scp", "-pr", file, f"{target_user}@{target_ip_addr}:{target_path}"],
            stderr=subprocess.PIPE,
        )
    except Exception as err:
        messages.print_err(
            "SSH connection could not be established. Check if the SSH keys are correct, see the following error:"
        )
        print(f"{err=}")
