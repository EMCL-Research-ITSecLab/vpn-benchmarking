import click
import json
import os
from error_messages import print_err, print_warn
import inquirer
from pathlib import Path

hosts = {"hosts": []}


@click.command()
@click.option("--server", default="", help="server: [user]@[ip_address]:[port]")
@click.option("--client", default="", help="client: [user]@[ip_address]")
def cli(server, client):
    # check if at both of the options is set
    # TODO: Add option to only enter one value
    if server == "" or client == "":
        click.echo(
            "Usage: set_hosts.py --server [user]@[ip_address]:[port] --client [user]@[ip_address]"
        )
        return

    # needed variables
    # server
    s_user = ""
    s_ip_addr = ""
    s_port = ""
    # client
    c_user = ""
    c_ip_addr = ""

    # get information about the server
    if server != "":
        try:
            s_user = server.split("@")[0]
            server = server.split("@")[1]
            s_ip_addr = server.split(":")[0]
            s_port = int(server.split(":")[1])

            server = {
                "role": "server",
                "ip_addr": s_ip_addr,
                "port": s_port,
                "user": s_user,
            }
            hosts["hosts"].append(server)
        except:
            print_err(
                "The format of the information about the server was incorrect. Correct format: [user]@[ip_address]:[port]"
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
                "The format of the information about the client was incorrect. Correct format: [user]@[ip_address]"
            )

    # save the data
    if os.path.exists("data/hosts.json"):  # file exists
        server_data_exists = False
        client_data_exists = False
        other_data_exists = False
        correct_data = False

        file = open("data/hosts.json")
        try:
            existing_data = json.load(file)
            # check what data the existing file contains
            for e in existing_data["hosts"]:
                correct_data = True
                if e["role"] == "server":
                    server_data_exists = True
                elif e["role"] == "client":
                    client_data_exists = True
                else:
                    other_data_exists = True
        except:
            existing_data = {}
            if correct_data:
                if not click.confirm("Delete existing file?"):
                    return

        file.close()

        # case 1: both entries exist
        if server_data_exists and client_data_exists:
            print_warn('The file "hosts.json" already exists.')
            if other_data_exists:
                questions = [
                    inquirer.List(
                        "keep",
                        choices=[
                            "keep existing file and do not update the information",
                            "keep existing data and update server and client information",
                            "delete existing data and update server and client information",
                        ],
                    ),
                ]
                answers = inquirer.prompt(questions)
                if answers != None:
                    if (
                        answers["keep"]
                        == "keep existing file and do not update the information"
                    ):
                        print("The information was not updated.")
                        return
                    elif (
                        answers["keep"]
                        == "keep existing data and update server and client information"
                    ):
                        for e in existing_data["hosts"]:
                            if e["role"] != "server" and e["role"] != "client":
                                hosts["hosts"].append(e)
                        os.remove("data/hosts.json")
                        Path("data").mkdir(parents=True, exist_ok=True)
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The server's information was updated to {s_user}@{s_ip_addr}:{s_port}."
                        )
                        print(
                            f"The client's information was updated to {c_user}@{c_ip_addr}."
                        )
                    elif (
                        answers["keep"]
                        == "delete existing data and update server and client information"
                    ):
                        os.remove("data/hosts.json")
                        Path("data").mkdir(parents=True, exist_ok=True)
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The server's information was updated to {s_user}@{s_ip_addr}:{s_port}."
                        )
                        print(
                            f"The client's information was updated to {c_user}@{c_ip_addr}."
                        )
                    else:
                        return
            else:
                questions = [
                    inquirer.List(
                        "keep",
                        choices=[
                            "keep existing file and do not update the information",
                            "update server and client information",
                        ],
                    ),
                ]
                answers = inquirer.prompt(questions)
                if answers != None:
                    if (
                        answers["keep"]
                        == "keep existing file and do not update the information"
                    ):
                        print("The information was not updated.")
                        return
                    elif answers["keep"] == "update server and client information":
                        os.remove("data/hosts.json")
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The server's information was updated to {s_user}@{s_ip_addr}:{s_port}."
                        )
                        print(
                            f"The client's information was updated to {c_user}@{c_ip_addr}."
                        )
                    else:
                        return
        # case 2: only one entry exists
        elif server_data_exists:
            print_warn('The file "hosts.json" already exists.')
            if other_data_exists:
                questions = [
                    inquirer.List(
                        "keep",
                        choices=[
                            "keep existing file and do not update the information",
                            "keep existing data and update server information",
                            "delete existing data and update server information",
                        ],
                    ),
                ]
                answers = inquirer.prompt(questions)
                if answers != None:
                    if (
                        answers["keep"]
                        == "keep existing file and do not update the information"
                    ):
                        print("The information was not updated.")
                        return
                    elif (
                        answers["keep"]
                        == "keep existing data and update server information"
                    ):
                        for e in existing_data["hosts"]:
                            if e["role"] != "server":
                                hosts["hosts"].append(e)
                        os.remove("data/hosts.json")
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The server's information was updated to {s_user}@{s_ip_addr}:{s_port}."
                        )
                    elif (
                        answers["keep"]
                        == "delete existing data and update server information"
                    ):
                        os.remove("data/hosts.json")
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The server's information was updated to {s_user}@{s_ip_addr}:{s_port}."
                        )
                    else:
                        return
            else:
                questions = [
                    inquirer.List(
                        "keep",
                        choices=[
                            "keep existing file and do not update the information",
                            "update server information",
                        ],
                    ),
                ]
                answers = inquirer.prompt(questions)
                if answers != None:
                    if (
                        answers["keep"]
                        == "keep existing file and do not update the information"
                    ):
                        print("The information was not updated.")
                        return
                    elif answers["keep"] == "update server information":
                        os.remove("data/hosts.json")
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The server's information was updated to {s_user}@{s_ip_addr}:{s_port}."
                        )
                    else:
                        return
        elif client_data_exists:
            print_warn('The file "hosts.json" already exists.')
            if other_data_exists:
                questions = [
                    inquirer.List(
                        "keep",
                        choices=[
                            "keep existing file and do not update the information",
                            "keep existing data and update client information",
                            "delete existing data and update client information",
                        ],
                    ),
                ]
                answers = inquirer.prompt(questions)
                if answers != None:
                    if (
                        answers["keep"]
                        == "keep existing file and do not update the information"
                    ):
                        print("The information was not updated.")
                        return
                    elif (
                        answers["keep"]
                        == "keep existing data and update client information"
                    ):
                        for e in existing_data["hosts"]:
                            if e["role"] != "client":
                                hosts["hosts"].append(e)
                        os.remove("data/hosts.json")
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The client's information was updated to {c_user}@{c_ip_addr}."
                        )
                    elif (
                        answers["keep"]
                        == "delete existing data and update client information"
                    ):
                        os.remove("data/hosts.json")
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The client's information was updated to {c_user}@{c_ip_addr}."
                        )
                    else:
                        return
            else:
                questions = [
                    inquirer.List(
                        "keep",
                        choices=[
                            "keep existing file and do not update the information",
                            "update client information",
                        ],
                    ),
                ]
                answers = inquirer.prompt(questions)
                if answers != None:
                    if (
                        answers["keep"]
                        == "keep existing file and do not update the information"
                    ):
                        print("The information was not updated.")
                        return
                    elif answers["keep"] == "update client information":
                        os.remove("data/hosts.json")
                        with open(f"data/hosts.json", "a") as file:
                            json.dump(hosts, indent=2, fp=file)
                        print(
                            f"The client's information was updated to {c_user}@{c_ip_addr}."
                        )
                    else:
                        return
        # case 3: no entries exist
        else:
            os.remove("data/hosts.json")
            with open(f"data/hosts.json", "a") as file:
                json.dump(hosts, indent=2, fp=file)
            print(f"The server's information was set to {s_user}@{s_ip_addr}:{s_port}.")
            print(f"The client's information was set to {c_user}@{c_ip_addr}.")
    else:  # file does not exist
        Path("data").mkdir(parents=True, exist_ok=True)
        with open(f"data/hosts.json", "a") as file:
            json.dump(hosts, indent=2, fp=file)
        print(f"The server's information was set to {s_user}@{s_ip_addr}:{s_port}.")
        print(f"The client's information was set to {c_user}@{c_ip_addr}.")

    if os.path.exists("ansible_files/hosts"):
        if click.confirm(
            "\nDerive ansible hosts file (this will overwrite the existing file)?"
        ):
            derive_ansible_hosts(s_user, s_ip_addr, c_user, c_ip_addr)
    else:
        if click.confirm("\nDerive ansible hosts file?"):
            derive_ansible_hosts(s_user, s_ip_addr, c_user, c_ip_addr)


def derive_ansible_hosts(s_user, s_ip_addr, c_user, c_ip_addr):
    if os.path.exists("ansible_files/hosts"):
        os.remove("ansible_files/hosts")

    Path("ansible_files").mkdir(parents=True, exist_ok=True)
    with open("ansible_files/hosts", "a") as file:
        file.write("[senders]\n")
        file.write(f"server ansible_host={s_ip_addr} ansible_user={s_user}\n\n")
        file.write("[receivers]\n")
        file.write(f"client ansible_host={c_ip_addr} ansible_user={c_user}")


if __name__ == "__main__":
    cli()