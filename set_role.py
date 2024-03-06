from helpers.messages import print_err, print_log
import click
import os
from pathlib import Path


def set_up_folder_structure(host):
    print("Setting up folder structure for rosenpass keys... ", end="", flush=True)
    try:
        base_path = os.getcwd()
        if host == "server":
            Path(base_path, "rp-keys", "client-public").mkdir(
                parents=True, exist_ok=True
            )
            print("done.")
            print_log("This device now has role server.")
        elif host == "client":
            Path(base_path, "rp-keys", "server-public").mkdir(
                parents=True, exist_ok=True
            )
            print("done.")
            print_log("This device now has role client.")
        else:
            print("failed.")
            print_err("ROLE must be server or client.")
    except:
        print("failed.")
        print_err("Could not set up folder structure.")


@click.command()
@click.argument("role")
def cli(role):
    set_up_folder_structure(role)


if __name__ == "__main__":
    cli()
