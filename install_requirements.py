import subprocess
from messages import print_err
import click
import os
from pathlib import Path


def install_pip_requirements():
    print("Installing pip requirements... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "-r", "requirements.txt"])
        print("done.")
    except:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-click"])
        except:
            print("failed.")
            print_err("Could not install requirements.")


def install_python_requirements():
    print("Installing python requirements... ", end="", flush=True)
    try:
        subprocess.check_output(["sudo", "apt-get", "install", "python3-pycurl"])
        subprocess.check_output(["sudo", "apt", "install", "libcurl4-gnutls-dev", "librtmp-dev"])
        print("done.")
    except:
        print("failed.")
        print_err("Could not install requirements.")


def set_up_folder_structure(host):
    print("Setting up folder structure for rosenpass keys... ", end="", flush=True)
    try:
        base_path = os.getcwd()
        if host == "server":
            Path(base_path, "rp-keys", "client-public").mkdir(
                parents=True, exist_ok=True
            )
            print("done.")
        elif host == "client":
            Path(base_path, "rp-keys", "server-public").mkdir(
                parents=True, exist_ok=True
            )
            print("done.")
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
    install_pip_requirements()
    install_python_requirements()
    cli()
