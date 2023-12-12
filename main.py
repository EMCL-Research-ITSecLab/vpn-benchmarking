from Monitoring import Monitoring
from HTTPExchange import HTTPExchange
from error_messages import print_err

import click


def client_genkeys(number):
    client = HTTPExchange.OnClient()
    client.gen_keys(number)


def client_share_keys(remote_dir):
    client = HTTPExchange().OnClient()
    client.send_public_keys_to_server(remote_dir)


def client_novpn_exchange(iterations, auto=False):
    monitor = Monitoring("client_novpn")
    client = HTTPExchange.OnClient()

    monitor.start(auto=auto)
    ### start test
    client.run(iterations, monitor=monitor)
    ### end test
    monitor.stop()


def client_rp_exchange(iterations=None, auto=False):
    monitor = Monitoring("client_rp_exchange")
    client = HTTPExchange.OnClient()

    monitor.start(auto=auto)
    ### start test
    client.run_with_rp(iterations=iterations, monitor=monitor)
    ### end test
    monitor.stop()


def server_genkeys(number=100):
    server = HTTPExchange.OnServer()
    server.gen_keys(number)


def server_share_keys(remote_dir):
    server = HTTPExchange().OnServer()
    server.send_public_keys_to_client(remote_dir)


def server_novpn_exchange(iterations, auto=False):
    monitor = Monitoring("server-novpn")
    server = HTTPExchange.OnServer()

    monitor.start(auto=auto)
    ### start test
    server.run(iterations, monitor=monitor)
    ### end test
    monitor.stop()


def server_rp_exchange(iterations=None, auto=False):
    monitor = Monitoring("server-rp")
    server = HTTPExchange.OnServer()

    monitor.start(auto=auto)
    ### start test
    server.run_with_rp(iterations=iterations, monitor=monitor)
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
@click.option("-i", "--iterations", type=int, default=1, help="number of iterations")
@click.option("--auto", type=bool, default=False, help="monitor in auto mode")
@click.option(
    "-d", "--dir", type=str, help="directory to save the keys (only for keysend option)"
)
@click.argument("operation", type=str)
def cli(role, iterations, operation, dir, auto):
    # TODO: Check if hosts file is correct

    if role == None:
        print("Missing option --server/--client for the role of the host.")
    elif role == "server":
        if operation == "keygen":
            server_genkeys(iterations)
        elif operation == "keysend":
            if dir != None:
                try:
                    server_share_keys(dir)
                except:
                    print_err("Directory could not be reached.")
            else:
                print_err(
                    "Missing directory for the keys on the remote host (use option -d)."
                )
        elif operation == "novpn":
            server_novpn_exchange(iterations, auto)
        elif operation == "rp":
            server_rp_exchange(iterations, auto)
        else:
            print("OPERATION must be keygen/keysend/novpn/rp.")
    elif role == "client":
        if operation == "keygen":
            client_genkeys(iterations)
        elif operation == "keysend":
            if dir != None:
                try:
                    client_share_keys(dir)
                except:
                    print_err("Directory could not be reached.")
            else:
                print_err(
                    "Missing directory for the keys on the remote host (use option -d)."
                )
        elif operation == "novpn":
            client_novpn_exchange(iterations, auto)
        elif operation == "rp":
            client_rp_exchange(iterations, auto)
        else:
            print("OPERATION must be keygen/keysend/novpn/rp.")
    else:
        return


if __name__ == "__main__":
    cli()