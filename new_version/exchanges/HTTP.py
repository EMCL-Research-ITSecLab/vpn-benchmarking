from new_version.Exchange import Exchange
import messages

from http.server import BaseHTTPRequestHandler, HTTPServer


class HTTP(Exchange):
    def __init__(self, role, server_name, server_port) -> None:
        super().__init__(role, server_name, server_port)

    def run(self) -> bool:
        if self.role == "server":
            try:
                server = HTTPServer((self.server_name, self.server_port), HTTP.Server)
                print("Awaiting request... ", end="", flush=True)
                server.handle_request()

                messages.print_log("Closing server.")
                server.server_close()
            except Exception as err:
                messages.print_err("Something went wrong while running the HTTP exchange.")
                print(f"{err=}")
                return False

            return True
    
        # TODO: Implement client behavior
        return False

    class Server(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
