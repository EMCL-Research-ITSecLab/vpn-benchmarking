import helpers.messages as messages

import subprocess


def send_file_to_host(file, target_user, target_ip_addr, target_path) -> bool:
    try:
        subprocess.check_output(
            ["scp", "-pr", file, f"{target_user}@{target_ip_addr}:{target_path}"],
            stderr=subprocess.PIPE,
        )
    except Exception as err:
        messages.print_err(
            "SSH connection could not be established. Check if the SSH keys are correct, see the following error:"
        )
        print(f"{err=}")
        return False

    return True
