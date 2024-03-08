import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO

import pycurl

import src.messages as messages
from src.exchanges.Exchange import Exchange


class HTTP(Exchange):
    def __init__(self, role, open_server_address, interface) -> None:
        super().__init__(role, open_server_address, 80, interface)

    def run(self) -> bool:
        if self.role == "server":
            try:
                server = HTTPServerV6((self.open_server_address, self.open_server_port), HTTP.Server)
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
            buffer = BytesIO()
            url = f"http://{self.open_server_address}:{self.open_server_port}"
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPGET, True)

            # if the VPN uses a different interface, get its name
            if self.interface:
                c.setopt(pycurl.INTERFACE, self.interface)

            c.setopt(pycurl.TIMEOUT, 10)
            c.setopt(pycurl.WRITEDATA, buffer)

            try:
                c.perform()
                response_code = c.getinfo(pycurl.RESPONSE_CODE)
                c.close()

                if response_code == 200:
                    messages.print_log("Request successful!")
                    return True
                else:
                    return False
            except:
                return False

        return False

    class Server(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()


class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6
