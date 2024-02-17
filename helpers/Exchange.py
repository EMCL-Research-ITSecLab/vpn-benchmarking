from http import server
from wsgiref.simple_server import server_version
import helpers.messages as messages


class Exchange:
    def __init__(self, role, server_name, server_port) -> None:
        self.role = None
        self.server_name = server_name
        self.server_port = server_port

        if role not in ("server", "client"):
            messages.print_err(
                "Unable to initialize exchange: unknown role. Known: server, client"
            )
            return
        else:
            self.role = role
            return

    def run(self) -> bool:
        messages.print_err("Exchange.run(self): NOT IMPLEMENTED")
        return False
