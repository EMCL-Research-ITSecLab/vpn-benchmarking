from ast import expr_context
import click
import json
from error_messages import print_err

hosts = {"hosts": []}


@click.command()
@click.option("--server", default="", help="server: [USER]@[IP ADDRESS]:[PORT]")
@click.option("--client", default="", help="client: [USER]@[IP ADDRESS]")
def cli(server, client):
    # check if at least one of the options is set
    if server == "" and client == "":
        click.echo(
            "Usage: set_hosts.py --server [USER]@[IP ADDRESS]:[PORT] --client [USER]@[IP ADDRESS]"
        )
        click.echo("It is possible to only pass one of options as arguments.")
        return

    # get information about the server
    if server != "":
        try:
            user = server.split("@")[0]
            server = server.split("@")[1]
            ip_addr = server.split(":")[0]
            port = server.split(":")[1]

            server = {"ip_addr": ip_addr, "port": port, "user": user}
            hosts["hosts"].append(server)
            print(
                f"The server's information was set/updated to {user}@{ip_addr}:{port}."
            )
        except:
            print_err(
                "The format of the information about the server was incorrect. Correct format: [USER]@[IP ADDRESS]:[PORT]"
            )

    # get information about the client
    if client != "":
        try:
            user = client.split("@")[0]
            ip_addr = client.split("@")[1]

            client = {"ip_addr": ip_addr, "user": user}
            hosts["hosts"].append(client)
            print(f"The client's information was set/updated to {user}@{ip_addr}.")
        except:
            print_err(
                "The format of the information about the client was incorrect. Correct format: [USER]@[IP ADDRESS]"
            )


if __name__ == "__main__":
    cli()
