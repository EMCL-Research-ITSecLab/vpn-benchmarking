import datetime


def print_err(message):
    print(f"[{datetime.datetime.now().isoformat()}", "\033[91mERROR\033[0m]", message)


def print_warn(message):
    print(f"[{datetime.datetime.now().isoformat()}", "\033[93mWARNING\033[0m]", message)
