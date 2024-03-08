import helpers.messages as messages


class Exchange:
    def __init__(self, role, open_server_address, open_server_port=9999, interface=None) -> None:
        self.open_server_address = open_server_address
        self.open_server_port = open_server_port
        self.interface = interface

        if role not in ("server", "client"):
            messages.print_err(
                "Unable to initialize exchange: unknown role. Known: server, client"
            )
            raise Exception("Unknown role")
        else:
            self.role = role

    def run(self) -> bool:
        messages.print_err("Exchange.run(self): NOT IMPLEMENTED")
        return False
