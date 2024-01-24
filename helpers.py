import messages
import os


def generate_rosenpass_keys(host, iterations):
    if host != "server" and host != "client":
        messages.print_err("Could not generate Rosenpass key set: Unknown host name as input.")
        return

    if iterations == 1:
        messages.print_log("Generating Rosenpass and Wireguard key set for server...")

        home_path = os.getcwd()


def count_rosenpass_keys():
    pass


def send_file_to_host():
    pass
