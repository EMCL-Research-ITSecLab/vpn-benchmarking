from new_version.Server import *
from new_version.Client import *
from new_version.vpns import NoVPN, Rosenpass
from new_version.exchanges import HTTP
import messages

import click


class HandleInput:
    valid_inputs = False

    def __init__(
        self, role, vpn_option, exchange_type, operation, iterations, dir
    ) -> None:
        self.role = role
        self.vpn_option = vpn_option
        self.exchange_type = exchange_type
        self.operation = operation
        self.iterations = iterations
        self.directory = dir

        if self.__check_values():
            self.valid_inputs = True

    def execute(self) -> bool:
        if not self.valid_inputs:
            messages.print_err("Inputs are not valid. Please start again.")
            return False

        if not self.__create_instance():
            return False

        if self.operation == "keygen":
            if not self.__handle_keygen():
                return False
        elif self.operation == "keysend":
            if not self.__handle_keysend():
                return False
        elif self.operation == "exchange":
            if not self.__handle_exchange():
                return False
        else:  # can not happen as long as values were checked and not changed
            return False
        return True

    def __check_values(self) -> bool:
        if self.role not in ("server", "client"):
            messages.print_err("Invalid ROLE argument. Has to be server|client.")
            return False

        if self.vpn_option not in ("novpn", "rosenpass"):
            messages.print_err(
                "Invalid VPN_OPTION argument. Has to be novpn|rosenpass."
            )
            return False

        if self.exchange_type not in ("http"):
            messages.print_err("Invalid EXCHANGE_TYPE argument. Has to be http.")
            return False

        if self.operation not in ("keygen", "keysend", "exchange"):
            messages.print_err(
                "Invalid OPERATION argument. Has to be keygen|keysend|exchange."
            )
            return False

        if self.iterations < 1:
            messages.print_err("Invalid ITERATIONS option. Has to be positive.")
            return False

        return True

    def __create_instance(self) -> bool:
        if self.role == "server":
            match self.exchange_type:
                case "http":
                    match self.vpn_option:
                        case "novpn":
                            self.instance = Server(HTTP, NoVPN)
                            return True
                        case "rosenpass":
                            self.instance = Server(HTTP, Rosenpass)
                            return True
                        case _:
                            return False
                case _:
                    return False
        elif self.role == "client":
            match self.exchange_type:
                case "http":
                    match self.vpn_option:
                        case "novpn":
                            self.instance = Client(HTTP, NoVPN)
                            return True
                        case "rosenpass":
                            self.instance = Client(HTTP, Rosenpass)
                            return True
                        case _:
                            return False
                case _:
                    return False
        else:
            return False

    def __handle_keygen(self):
        self.instance.keygen()

    def __handle_keysend(self):
        self.instance.keysend(self.directory)

    def __handle_exchange(self):
        self.instance.run(self.iterations)


# EXCHANGE:
# python main.py
#   -i|--iterations 100
#   server|client
#   novpn|rosenpass
#   http
#   exchange

# KEY GENERATION:
# python main.py
#   server|client
#   novpn|rosenpass
#   http
#   keygen

# SENDING PUBLIC KEYS:
# python main.py
#   server|client
#   novpn|rosenpass
#   http
#   keysend


@click.command()
@click.option("-i", "--iterations", type=int, default=1, help="number of iterations")
@click.option(
    "-d", "--dir", type=str, help="directory to save the keys (only for keysend option)"
)
@click.argument("role", type=str)
@click.argument("vpn_option", type=str)
@click.argument("exchange_type", type=str)
@click.argument("operation", type=str)
def cli(role, vpn_option, exchange_type, operation, iterations, dir):
    return (role, vpn_option, exchange_type, operation, iterations, dir)


if __name__ == "__main__":
    inputs = cli()
    handler = HandleInput(
        inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5]
    )
