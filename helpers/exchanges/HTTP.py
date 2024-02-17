from helpers.Exchange import Exchange
import helpers.messages as messages

from http.server import BaseHTTPRequestHandler, HTTPServer
import pycurl


class HTTP(Exchange):
    def __init__(self, role, server_name, server_port) -> None:
        super().__init__(role, server_name, server_port)

    def run(self) -> bool:
        # TODO: Add monitor

        if self.role == "server":
            try:
                server = HTTPServer((self.server_name, self.server_port), HTTP.Server)
                print("Awaiting request... ", end="", flush=True)
                server.handle_request()

                messages.print_log("Closing server.")
                server.server_close()
            except Exception as err:
                messages.print_err(
                    "Something went wrong while running the HTTP exchange (server)."
                )
                print(f"{err=}")
                return False
            return True
        if self.role == "client":
            try:
                url = f"http://{self.server_name}:{self.server_port}"
                c = pycurl.Curl()
                c.setopt(pycurl.URL, url)
                c.setopt(pycurl.HTTPGET, True)
                c.setopt(pycurl.TIMEOUT, 10)
                c.perform()
                c.close()
            except Exception as err:
                messages.print_err(
                    "Something went wrong while running the HTTP exchange (client)."
                )
                print(f"{err=}")
                return False
            return True

        return False

    class Server(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
