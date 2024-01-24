import messages
import os
import subprocess


class Rosenpass:
    def __init__(self, role) -> None:
        if role not in ("server", "client"):
            messages.print_err("Unknown role as input.")
            self.role = None
            return

        self.role = role
        self.home_path = os.getcwd()

    def generate_keys(self, iterations):
        if self.role == None:
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

    def count_keys(self):
        pass


def send_file_to_host():
    pass
