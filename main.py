from os import error
import subprocess
from traitlets import default
from Monitoring import Monitoring
from HTTPExchange import HTTPExchange
from error_messages import print_err

import click

# TODO: Let rp use iterations too


def client_genkeys(number=100):
    client = HTTPExchange.OnClient()
    client.gen_keys(number)


def client_novpn_exchange(iterations=100, auto=False):
    monitor = Monitoring("client_novpn")
    client = HTTPExchange.OnClient()

    monitor.start(auto=auto)
    ### start test
    client.run(iterations, monitor=monitor)
    ### end test
    monitor.stop()


def client_rp_exchange(iterations=100, auto=False):
    monitor = Monitoring("client_rp_exchange")
    client = HTTPExchange.OnClient()

    monitor.start(auto=auto)
    ### start test
    client.run_with_rp(monitor=monitor)
    ### end test
    monitor.stop()


def server_genkeys(number=100):
    server = HTTPExchange.OnServer()
    server.gen_keys(number)


def server_novpn_exchange(iterations=100, auto=False):
    monitor = Monitoring("server-novpn")
    server = HTTPExchange.OnServer()

    monitor.start(auto=auto)
    ### start test
    server.run(iterations, monitor=monitor)
    ### end test
    monitor.stop()


def server_rp_exchange(iterations=100, auto=False):
    monitor = Monitoring("server-rp")
    server = HTTPExchange.OnServer()

    monitor.start(auto=auto)
    ### start test
    server.run_with_rp(monitor=monitor)
    ### end test
    monitor.stop()


# EXAMPLES:
# python main.py --role server -i 100                  # execute exchange for server with 100 iterations
# python main.py genkeys --role server -i 100          # generate 100 keys for server
# python main.py genkeys -r server --iterations 100    # generate 100 keys for server
# python main.py genkeys -r server -i 50               # generate 50 keys for server


@click.command()
@click.option("--server", "role", flag_value="server")
@click.option("--client", "role", flag_value="client")
@click.option(
    "-i", "--iterations", required=True, type=int, help="number of iterations"
)
@click.argument("operation", type=str)
def cli(role, iterations, operation):
    # TODO: Check if hosts file is correct

    if role == None:
        print("Missing option --server/--client for the role of the host.")
    elif role == "server":
        if operation == "genkeys":
            server_genkeys(iterations)
        elif operation == "novpn":
            server_novpn_exchange(iterations)
        elif operation == "rp":
            server_rp_exchange(iterations)
        else:
            print("OPERATION must be genkeys/novpn/rp.")
    elif role == "client":
        if operation == "genkeys":
            client_genkeys(iterations)
        elif operation == "novpn":
            client_novpn_exchange(iterations)
        elif operation == "rp":
            client_rp_exchange(iterations)
        else:
            print("OPERATION must be genkeys/novpn/rp.")
    else:
        return


def install_requirements():
    print("Installing pip requirements... ", end='', flush=True)
    try:
        subprocess.check_output(["pip", "install", "-r", "requirements.txt"])
        print("done.")
    except:
        print_err("Could not install requirements.")

if __name__ == "__main__":
    install_requirements()
    cli()
