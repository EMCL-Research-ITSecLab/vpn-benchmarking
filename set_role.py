import os
from pathlib import Path

import click

from src.messages import print_err, print_log


def set_up_folder_structure(host) -> None:
    """
    Creates the key (sub)directories.
    :param host: role of the host
    """
    print("Setting up folder structure for rosenpass keys... ", end="", flush=True)
    try:
        base_path = os.getcwd()
        if host == "server":
            Path(base_path, "rp-keys", "client.rosenpass-public").mkdir(
                parents=True, exist_ok=True
            )
            print("done.")
            print_log("This device now has role server.")
        elif host == "client":
            Path(base_path, "rp-keys", "server.rosenpass-public").mkdir(
                parents=True, exist_ok=True
            )
            print("done.")
            print_log("This device now has role client.")
        else:
            print("failed.")
            print_err("ROLE must be server or client.")
    except Exception as err:
        print("failed.")
        print_err("Could not set up folder structure.")
        print(f"{err=}")


@click.command()
@click.argument("role")
def cli(role):
    """
    :param role: role of the host
    """
    set_up_folder_structure(role)


if __name__ == "__main__":
    cli()
