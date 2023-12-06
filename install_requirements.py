import subprocess
from error_messages import print_err


def install_pip_requirements():
    print("Installing pip requirements... ", end="", flush=True)
    try:
        subprocess.check_output(["pip", "install", "-r", "requirements.txt"])
        print("done.")
    except:
        print_err("Could not install requirements.")


if __name__ == "__main__":
    install_pip_requirements()
