import datetime

"""
Specifies the message formats in different cases.
"""


def print_log(message):
    """
    Message in 'normal' case. Logging information. Adds a timestamp.
    :param message: message of the log
    """
    print(f"[{datetime.datetime.now().isoformat()}]", message)


# warning messages
def print_warn(message):
    """
    Message as a warning. Used for not critical warnings. Adds a timestamp.
    :param message: message of the warning
    """
    print(f"[{datetime.datetime.now().isoformat()}", "\033[93mWARNING\033[0m]", message)


# error messages
def print_err(message):
    """
    Message as an error. Used for errors and exceptions. Adds a timestamp.
    :param message: description of the error
    """
    print(f"[{datetime.datetime.now().isoformat()}", "\033[91mERROR\033[0m]", message)
