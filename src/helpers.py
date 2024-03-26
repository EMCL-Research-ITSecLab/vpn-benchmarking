import subprocess

import src.messages as messages

"""
Contains any functions that are universal in a way that they can be used by multiple classes can be put here.
"""


def send_file_to_host(file, target_user, target_ip_addr, target_path) -> bool:
    """
    Sends the given file to a remote host with the given username and IP address into the given remote directory.
    :param file: file to be sent
    :param target_user: username on the remote host
    :param target_ip_addr: IP address of the remote host
    :param target_path: directory for putting the file in on the remote host
    :return: True for success, False otherwise
    """
    try:
        subprocess.check_output(
            ["scp", "-pr", file, f"{target_user}@{target_ip_addr}:{target_path}"],
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        messages.print_err(
            "SSH connection could not be established. Check if the SSH keys are correct."
        )
        return False
    except Exception as err:
        print(f"{err=}")
        return False
