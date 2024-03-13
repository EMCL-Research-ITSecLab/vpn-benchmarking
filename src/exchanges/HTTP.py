import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO

import pycurl

import src.messages as messages
from src.exchanges.Exchange import Exchange


class HTTP(Exchange):
    """
    Implements an HTTP exchange. The server opens port 80 and waits. The client sends one HTTP GET packet and expects
    a '200 OK' response. The server closes after handling the packet.
    """

    def __init__(self, role, open_server_address, interface) -> None:
        """
        :param role: role of the host
        :param open_server_address: address to be opened on the server, or already open for the client
        :param interface: name of the interface for the client to use
        """
        super().__init__(role, open_server_address, 80, interface)

    def run(self) -> int:
        """
        Decides what is executed based on the role.
        :return: 0 for success, 1 for an error that can be solved by running again, 2 for an error that requires
        reopening the interface
        """
        if self.role == "server":
            return self.__run_server(self.open_server_address, self.open_server_port)
        elif self.role == "client":
            return self.__run_client(self.open_server_address, self.open_server_port, self.interface)

        return 1  # if role was not server or client

    @staticmethod
    def __run_server(address, port) -> int:
        """
        Creates the IPv6 HTTP Server and waits for one request. Closes afterward.
        :param address: address for opening the server
        :param port: port for opening the server
        :return: 0 for success, 1 otherwise
        """
        try:
            server = HTTPServerV6((address, port), HTTP.RequestHandler)

            print("Awaiting request... ", end="", flush=True)
            server.handle_request()

            messages.print_log("Closing server.")
            server.server_close()
            return 0
        except Exception as err:
            messages.print_err(
                "Something went wrong while running the HTTP exchange (server)."
            )
            print(f"{err=}")
            return 1

    @staticmethod
    def __run_client(address, port, interface) -> int:
        """
        Generates the GET packet for the server. Specifies the interface to be used for sending, if a VPN is used.
        Expects '200 OK' response.
        :param address: address on which the server runs
        :param port: open server port
        :param interface: interface to be used for transmission, has to exist
        :return: 0 for success, 1 for an error that can be solved by running again, 2 for an error that requires
        reopening the interface
        """
        buffer = BytesIO()  # buffer for storing response

        url = f"http://{address}:{port}"

        # set Curl parameters
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPGET, True)

        # if the VPN uses a different interface, get its name
        if interface:
            c.setopt(pycurl.INTERFACE, interface)

        c.setopt(pycurl.TIMEOUT, 2)
        c.setopt(pycurl.WRITEDATA, buffer)

        try:
            c.perform()
            response_code = c.getinfo(pycurl.RESPONSE_CODE)
            c.close()
        except pycurl.error as e:
            if "28" in str(e):  # 28 is the error code for timeouts
                return 2
            return 1

        if response_code == 200:
            messages.print_log("Request successful!")
            return 0

        return 1

    class RequestHandler(BaseHTTPRequestHandler):
        """
        Specifies the response to a GET packet. Only sends '200 OK'.
        """

        def do_GET(self):
            self.send_response(200)
            self.end_headers()


class HTTPServerV6(HTTPServer):
    """
    Normal HTTP Server using IPv6.
    """
    address_family = socket.AF_INET6
