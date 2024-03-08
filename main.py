import click

from helpers.Client import *
from helpers.Monitoring import Monitoring
from helpers.Server import *
from helpers.exchanges.HTTP import *
from helpers.vpns.NoVPN import *
from helpers.vpns.Rosenpass import *


class HandleInput:
    valid_inputs = False

    def __init__(
            self, role, vpn_option, exchange_type, operation, iterations, directory, auto
    ) -> None:
        self.role = role
        self.vpn_option = vpn_option
        self.exchange_type = exchange_type
        self.operation = operation
        self.iterations = iterations
        self.directory = directory
        self.auto = auto

        if self.__check_values():
            self.valid_inputs = True

    def execute(self) -> bool:
        if not self.valid_inputs:
            helpers.messages.print_err("Inputs are not valid. Please start again.")
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
        else:
            return False
        return True

    def __check_values(self) -> bool:
        if self.role not in ("server", "client"):
            helpers.messages.print_err(
                "Invalid ROLE argument. Has to be server|client."
            )
            return False

        if self.vpn_option not in ("novpn", "rosenpass"):
            helpers.messages.print_err(
                "Invalid VPN_OPTION argument. Has to be novpn|rosenpass."
            )
            return False

        if self.exchange_type not in ("http"):
            helpers.messages.print_err(
                "Invalid EXCHANGE_TYPE argument. Has to be http."
            )
            return False

        if self.operation not in ("keygen", "keysend", "exchange"):
            helpers.messages.print_err(
                "Invalid OPERATION argument. Has to be keygen|keysend|exchange."
            )
            return False

        if self.iterations < 1:
            helpers.messages.print_err("Invalid ITERATIONS option. Has to be positive.")
            return False

        return True

    def __create_instance(self) -> bool:
        if self.role == "server":
            if self.exchange_type == "http":
                if self.vpn_option == "novpn":
                    self.instance = Server(HTTP, NoVPN)
                    return True
                elif self.vpn_option == "rosenpass":
                    self.instance = Server(HTTP, Rosenpass)
                    return True
                else:
                    return False
            else:
                return False
        elif self.role == "client":
            if self.exchange_type == "http":
                if self.vpn_option == "novpn":
                    self.instance = Client(HTTP, NoVPN)
                    return True
                elif self.vpn_option == "rosenpass":
                    self.instance = Client(HTTP, Rosenpass)
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def __handle_keygen(self):
        self.instance.keygen()

    def __handle_keysend(self):
        self.instance.keysend(self.directory)

    def __handle_exchange(self):
        monitor = Monitoring(self.role, self.vpn_option)

        monitor.start(auto=self.auto)
        ### start test
        self.instance.run(self.iterations, monitor)
        ### end test
        monitor.stop()


@click.command()
@click.option("-i", "--iterations", type=int, default=1, help="number of iterations")
@click.option(
    "-d",
    "--directory",
    type=str,
    help="directory to save the keys (only for keysend option)",
    default="~",
)
@click.option("--auto", help="monitor in auto mode", is_flag=True)
@click.argument("role", type=str)
@click.argument("vpn_option", type=str)
@click.argument("exchange_type", type=str)
@click.argument("operation", type=str)
def cli(role, vpn_option, exchange_type, operation, iterations, directory, auto):
    handler = HandleInput(
        role, vpn_option, exchange_type, operation, iterations, directory, auto
    )
    handler.execute()


if __name__ == "__main__":
    cli()
