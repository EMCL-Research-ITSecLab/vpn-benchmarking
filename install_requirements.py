import subprocess
from error_messages import print_err
import click
import os
from pathlib import Path


def install_pip_requirements():
    print("Installing pip requirements... ", end="", flush=True)
    try:
        subprocess.check_output(["pip", "install", "-r", "requirements.txt"])
        print("done.")
    except:
        print_err("Could not install requirements.")


def set_up_folder_structure(host):
    # TODO: Remove folder rp-exchange from all files
    print("Setting up folder structure for rosenpass keys... ", end="", flush=True)
    try:
        base_path = os.getcwd()
        if host == "server":
            Path(base_path, "rp-exchange/rp-keys", "client-public").mkdir(
                parents=True, exist_ok=True
            )
            print("done.")
        elif host == "client":
            Path(base_path, "rp-exchange/rp-keys", "server-public").mkdir(
                parents=True, exist_ok=True
            )
            print("done.")
        else:
            print_err("ROLE must be server or client.")
    except:
        print_err("Could not install requirements.")


@click.command()
@click.argument("role")
def cli(role):
    set_up_folder_structure(role)


if __name__ == "__main__":
    install_pip_requirements()
    cli()
