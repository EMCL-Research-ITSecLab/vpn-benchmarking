import subprocess

from src.messages import print_log, print_warn


def install_requirements() -> None:
    """
    Installs all requirements. Outputs success if all dependencies were installed. If one or more installations
    failed, outputs a warning.
    """
    print_log("Installing requirements...")
    successful = True

    if not install_click():
        successful = False
    if not install_inquirer():
        successful = False
    if not install_numpy():
        successful = False
    if not install_pycurl():
        successful = False
    if not install_psutil():
        successful = False

    if successful:
        print_log("All dependencies installed.")
        return

    print_warn("Not all dependencies could be installed!")


def install_psutil() -> bool:
    """
    Installs psutil to venv using pip.
    :return: True for success, False otherwise
    """
    print("Install psutil... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "psutil"])
    except FileNotFoundError:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-psutil"])
        except FileNotFoundError:
            print("failed.")
            return False

    print("done.")
    return True


def install_click() -> bool:
    """
    Installs click to venv using pip.
    :return: True for success, False otherwise
    """
    print("Install click... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "click"])
    except FileNotFoundError:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-click"])
        except FileNotFoundError:
            print("failed.")
            return False

    print("done.")
    return True


def install_inquirer() -> bool:
    """
    Installs inquirer to venv using pip.
    :return: True for success, False otherwise
    """
    print("Install inquirer... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "inquirer"])
    except FileNotFoundError:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-inquirer"])
        except FileNotFoundError:
            print("failed.")
            return False

    print("done.")
    return True


def install_numpy() -> bool:
    """
    Installs numpy to venv using pip.
    :return: True for success, False otherwise
    """
    print("Install numpy... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "numpy"])
    except FileNotFoundError:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-numpy"])
        except FileNotFoundError:
            print("failed.")
            return False

    print("done.")
    return True


def install_pycurl() -> bool:
    """
    Installs pycurl to venv using pip.
    :return: True for success, False otherwise
    """
    print("Install pycurl... ", end="", flush=True)

    try:
        subprocess.check_output(
            ["bin/pip", "install", "pycurl"],
        )
    except FileNotFoundError:
        try:
            subprocess.check_output(
                ["bin/pip", "install", "python3-pycurl"],
            )
        except FileNotFoundError:
            print("failed.")
            return False

    print("done.")
    return True


if __name__ == "__main__":
    install_requirements()
