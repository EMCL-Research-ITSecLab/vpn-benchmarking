import click
import json
import os
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
            s_user = server.split("@")[0]
            server = server.split("@")[1]
            s_ip_addr = server.split(":")[0]
            s_port = server.split(":")[1]

            server = {"role": "server", "ip_addr": s_ip_addr, "port": s_port, "user": s_user}
            hosts["hosts"].append(server)
            print(
                f"The server's information was set/updated to {s_user}@{s_ip_addr}:{s_port}."
            )
        except:
            print_err(
                "The format of the information about the server was incorrect. Correct format: [USER]@[IP ADDRESS]:[PORT]"
            )

    # get information about the client
    if client != "":
        try:
            c_user = client.split("@")[0]
            c_ip_addr = client.split("@")[1]

            client = {"role": "client", "ip_addr": c_ip_addr, "user": c_user}
            hosts["hosts"].append(client)
        except:
            print_err(
                "The format of the information about the client was incorrect. Correct format: [USER]@[IP ADDRESS]"
            )
            
    server_data_exists = False        
    client_data_exists = False        
    other_data_exists = False        
    
    # save the data
    if os.path.exists("data/hosts.json"):
        file = open("data/hosts.json")
        data = json.load(file)
        
        for e in data["hosts"]:
            if e["role"] == "server":
                server_data_exists = True
            elif e["role"] == "client":
                client_data_exists = True
            else:
                other_data_exists = True
        
        # case 1: both entries exist
        if server_data_exists and client_data_exists:
            # overwrite empty file after asking
            if click.confirm('Overwrite existing "hosts.json"?') == False:
                click.echo("The data has not been updated.")
                return
        # case 2: only one entry exists
        elif server_data_exists:
            if click.confirm('Overwrite existing server information in "hosts.json"?'):
                json.dump(hosts, indent=2, fp=file)
            else:
                
                click.echo("The server information was not updated.")
        elif client_data_exists:
            if click.confirm('Overwrite existing client information in "hosts.json"?'):
                click.echo("The client information was not updated.")
        # case 3: no entries exist
        else:
            with open(f"data/hosts.json", "w") as file:
                json.dump(hosts, indent=2, fp=file)


if __name__ == "__main__":
    cli()
