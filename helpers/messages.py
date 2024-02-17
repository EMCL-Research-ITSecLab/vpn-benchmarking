import datetime


# normal messages
def print_log(message):
    print(f"[{datetime.datetime.now().isoformat()}]", message)


# warning messages
def print_warn(message):
    print(f"[{datetime.datetime.now().isoformat()}", "\033[93mWARNING\033[0m]", message)


# error messages
def print_err(message):
    print(f"[{datetime.datetime.now().isoformat()}", "\033[91mERROR\033[0m]", message)
