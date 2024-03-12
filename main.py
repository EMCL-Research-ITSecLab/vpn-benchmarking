from src.Client import *
from src.Monitoring import Monitoring
from src.Server import *
from src.exchanges.HTTP import *
from src.vpns.NoVPN import *
from src.vpns.Rosenpass import *


class HandleInput:
    """
    Handles the inputs given.
    """
    valid_inputs = False

    def __init__(
            self, role, vpn_option, exchange_type, operation, iterations, directory, auto
    ) -> None:
        """
        Sets all values to the given inputs and checks the values.
        :param role: role of the host
        :param vpn_option: VPN type to be used
        :param exchange_type: Exchange type to be used
        :param operation: Operation to be executed
        :param iterations: number of iterations of exchanges
        :param directory: directory to save the keys (only for keysend option)
        :param auto: activates monitoring in automatic mode
        """
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
        """
        If inputs are valid, creates the server or client instance with the given parameters and executes the given
        operation.
        :return: True for success, False otherwise
        """
        if not self.valid_inputs:
            helpers.messages.print_err("Inputs are not valid. Please start again.")
            return False

        self.__create_instance()

        if self.operation == "keygen":
            self.__handle_keygen()
        elif self.operation == "keysend":
            self.__handle_keysend()
        elif self.operation == "exchange":
            self.__handle_exchange()

        return True

    def __check_values(self) -> bool:
        """
        Checks if the given inputs are in the defined scope. Returns False otherwise.
        :return: True for success, False otherwise
        """
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

        if not self.exchange_type == "http":
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

    def __create_instance(self) -> None:
        """
        Creates the server or client instance with the given parameters.
        """
        # create Exchange instance
        exchange = None
        if self.exchange_type == "http":
            exchange = HTTP

        # create VPN instance
        vpn = None
        if self.vpn_option == "novpn":
            vpn = NoVPN
        elif self.vpn_option == "rosenpass":
            vpn = Rosenpass

        if self.role == "server":
            self.instance = Server(exchange, vpn)
        elif self.role == "client":
            self.instance = Client(exchange, vpn)

    def __handle_keygen(self) -> None:
        """
        Handles the key generation.
        """
        self.instance.keygen()

    def __handle_keysend(self) -> None:
        """
        Handles the key sending.
        """
        self.instance.keysend(self.directory)

    def __handle_exchange(self) -> None:
        """
        Starts the monitor, executes the exchange and stops the monitor.
        """
        monitor = Monitoring(self.role, self.vpn_option)

        monitor.start(auto=self.auto)
        # start test
        self.instance.run(self.iterations, monitor)
        # end test
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
    """
    Calls the handler with the given CLI inputs.
    :param role: role of the host
    :param vpn_option: VPN type to be used
    :param exchange_type: Exchange type to be used
    :param operation: Operation to be executed
    :param iterations: number of iterations of exchanges
    :param directory: directory to save the keys (only for keysend option)
    :param auto: activates monitoring in automatic mode
    """
    handler = HandleInput(
        role, vpn_option, exchange_type, operation, iterations, directory, auto
    )
    if not handler.execute():
        messages.print_err("Execution failed.")


if __name__ == "__main__":
    cli()
