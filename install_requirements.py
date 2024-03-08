import subprocess

from src.messages import print_err, print_log


def install_requirements():
    print_log("Installing requirements...")
    if not install_click():
        return
    if not install_inquirer():
        return
    if not install_numpy():
        return
    if not install_pycurl():
        return
    if not install_psutil():
        return
    print_log("All dependencies installed.")


def install_psutil() -> bool:
    print("Install psutil... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "psutil"])
    except:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-psutil"])
        except:
            print("failed.")
            print_err(
                "Could not install requirements. Module 'psutil' could not be installed."
            )
            return False

    print("done.")
    return True


def install_click() -> bool:
    print("Install click... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "click"])
    except:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-click"])
        except:
            print("failed.")
            print_err(
                "Could not install requirements. Module 'click' could not be installed."
            )
            return False

    print("done.")
    return True


def install_inquirer() -> bool:
    print("Install inquirer... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "inquirer"])
    except:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-inquirer"])
        except:
            print("failed.")
            print_err(
                "Could not install requirements. Module 'inquirer' could not be installed."
            )
            return False

    print("done.")
    return True


def install_numpy() -> bool:
    print("Install numpy... ", end="", flush=True)
    try:
        subprocess.check_output(["bin/pip", "install", "numpy"])
    except:
        try:
            subprocess.check_output(["bin/pip", "install", "python3-numpy"])
        except:
            print("failed.")
            print_err(
                "Could not install requirements. Module 'numpy' could not be installed."
            )
            return False

    print("done.")
    return True


def install_pycurl() -> bool:
    print("Install pycurl... ", end="", flush=True)

    try:
        subprocess.check_output(
            ["bin/pip", "install", "pycurl"],
        )
    except:
        try:
            subprocess.check_output(
                ["bin/pip", "install", "python3-pycurl"],
            )
        except:
            print("failed.")
            print_err(
                "Could not install requirements. Module 'pycurl' could not be installed.\nRun 'sudo apt install libcurl4-gnutls-dev librtmp-dev && sudo apt install python3-pycurl && bin/pip install pycurl' manually."
            )
            return False

    print("done.")
    return True


if __name__ == "__main__":
    install_requirements()
