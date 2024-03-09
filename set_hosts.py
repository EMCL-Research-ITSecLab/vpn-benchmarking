import click

from src.HostsManager import HostsManager


# hosts = {"hosts": []}
# hosts_path = "hosts.json"


@click.command()
@click.option("--server", default="", help="server: [user]@[ip_address]")
@click.option("--client", default="", help="client: [user]@[ip_address]")
def cli(server, client) -> None:
    """
    Calls the handler for creating the hosts file from the input arguments.
    :param server: server information in the form [user]@[ip_address]
    :param client: client information in the form [user]@[ip_address]
    """
    # check if at both of the options is set
    if not (server and client):
        click.echo(
            "Usage: set_hosts.py --server [user]@[ip_address] --client [user]@[ip_address]"
        )
        return

    if not len(server.split("@")) == 2:
        click.echo(
            "Usage: set_hosts.py --server [user]@[ip_address] --client [user]@[ip_address]"
        )
        return

    if not len(client.split("@")) == 2:
        click.echo(
            "Usage: set_hosts.py --server [user]@[ip_address] --client [user]@[ip_address]"
        )
        return

    server_address = server.split("@")[1]
    client_address = client.split("@")[1]
    server_user = server.split("@")[0]
    client_user = client.split("@")[0]

    if not (
            server_user and client_user and server_address and client_address
    ):
        click.echo(
            "Usage: set_hosts.py --server [user]@[ip_address] --client [user]@[ip_address]"
        )
        return

    # create the hosts file
    HostsManager(server_address, client_address, server_user, client_user)


if __name__ == "__main__":
    cli()
