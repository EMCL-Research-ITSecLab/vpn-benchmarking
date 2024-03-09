import src.messages as messages


class Exchange:
    """
    Base class for exchanges. To add a new exchange type, a class must inherit from Exchange.
    """

    def __init__(self, role, open_server_address, open_server_port=9999, interface=None) -> None:
        """
        Loads all values needed for an exchange. Checks if the role is valid, throws an Exception otherwise.
        :param role: role of the host, server or client
        :param open_server_address: address on which the server will be reachable
        :param open_server_port: publicly reachable port to be opened, default: 9999
        :param interface: name of the interface of the VPN used during the exchange or None (default)
        """
        self.open_server_address = open_server_address
        self.open_server_port = open_server_port
        self.interface = interface

        if role not in ("server", "client"):
            messages.print_err(
                "Unable to initialize exchange: unknown role. Known: server, client"
            )
            raise Exception("Unexpected role")

        self.role = role

    def run(self) -> bool:
        """
        Executes the exchange with the set parameters. Implementation is done in inheriting classes.
        :return: False since not implemented
        """
        messages.print_err("Exchange.run(self): NOT IMPLEMENTED")
        return False
