import subprocess
from messages import print_err
import click
import os
from pathlib import Path


def set_up_venv():
    print("Setting up venv environment...")
    try:
        subprocess.check_output(["python", "-m", "venv", "."])
        print("done.")
    except:
        print("failed.")
        print_err("Could not install requirements.")


def install_pip_requirements():
    print("Installing pip requirements... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "-r", "requirements.txt"])
        print("done.")
    except:
        print("failed.")
        print_err("Could not install requirements.")


def install_python_requirements():
    print("Installing python requirements... ", flush=True)
    try:
        subprocess.check_output(["sudo", "apt-get", "install", "python3-pycurl"])
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
        print_err("Could not install requirements.")


@click.command()
@click.argument("role")
def cli(role):
    set_up_folder_structure(role)


if __name__ == "__main__":
    set_up_venv()
    install_pip_requirements()
    install_python_requirements()
    cli()
