# VPN Benchmarking

This project aims to measure and compare the performance overhead of using a VPN connection and to visualize the resulting data.

## Usage for Performance Measurements
### Installing libraries
As a first step, it is required to set up a virtual environment for the installation. For this, install `venv` on your machines and use
```
$ python -m venv DIRECTORY
```
with `DIRECTORY` being the working directory of the project.

Activate the environment in this directory by executing:
```
$ source bin/activate
```

Now, you need to install necessary libraries by executing the following command in the same folder in which you set up `venv`:
```
$ sudo python install_requirements.py
```

Set the device's role in the exchange by executing:
```
user@server:~$ python set_role.py server
```
```
user@client:~$ python set_role.py client
```

### Setting the hosts
Next, you need to define both hosts that take part in the exchange on all devices. For this, execute the command
```
$ python set_hosts.py --server USER@IP_ADDRESS:PORT --client USER@IP_ADDRESS
```
on the `server`, the `client` AND if Rosenpass needs to be installed, on a third host `master`. Alternatively, you can only run it on `server` and `client` and copy the derived ansible hosts file to the `master` manually.

`USER` and `IP_ADDRESS` describe the user and the IP address on the respective host, the port for opening the server needs to be specified as `PORT` in the server option (you should be able to use port 9999).
Note, that both options `--server` and `--client` have to be set on both hosts.

After setting the hosts, you will be asked if you want to set the same hosts for the ansible hosts file. This can be used in the next step, to install Rosenpass on the hosts. Confirm on `master` if you need to install or update Rosenpass. The file is not needed on `server` and `client`, but can be generated and copied to `master` if needed.

### Install latest Rosenpass version
For setting up the environment, install Ansible on a third device (master), set up SSH keys on both hosts, copy the ansible hosts file from one of the hosts to master and use:
```
user@master:~/ansible_files$ ansible-playbook install_rosenpass.yml --ask-become-pass
```
You will be asked to enter the password for the remote machine. At the moment, it is only possible to update machines with the same password by running the command once.

### Generate Rosenpass keys and share public keys
All the following functions can be used by executing `main.py` with different arguments and options.

#### Generating Rosenpass keys
To generate the necessary keys, use the command:
```
user@server:~$ python main.py server keygen [-i/--iterations ITERATIONS]
```
```
user@client:~$ python main.py client keygen [-i/--iterations ITERATIONS]
```
with `ITERATIONS` being the number of key sets that need to be generated. By default, this value is 1. By specifying the number of keys manually, you can create several different Rosenpass key sets. In the exchange, every connection will use a different key set. By setting the number to 1 (default), only one key will be generated and used in the exchange. The number of iterations can then be specified later when executing the exchange.

For a successful exchange, both hosts have to generate the same number of key sets.

#### Sharing Rosenpass public keys with the other host
For sharing the keys, it is necessary to set up SSH keys on both the server and the client. To share the keys, execute:
```
user@server:~$ python main.py server keysend -d REMOTE_CLIENT_DIRECTORY
```
```
user@client:~$ python main.py client keysend -d REMOTE_SERVER_DIRECTORY
```
`REMOTE_SERVER_DIRECTORY` and `REMOTE_CLIENT_DIRECTORY` specify the working directory on the remote host, in which the folder `rp-keys` for the keys is existent.

If an error occurs after execution, make sure you have the correct SSH keys set up and shared on the hosts and have enabled and started `ssh`. To make sure, run the commands on both hosts:
```
$ sudo systemctl enable ssh
$ sudo systemctl start ssh
```

### Execute HTTP exchange
Now the keys and hosts should be ready to start and monitor exchanges.

#### HTTP exchange using no vpn (baseline)
Start the baseline HTTP exchange, by running the following commands:
```
user@server:~$ python main.py server novpn -i/--iterations ITERATIONS [--auto]
```
```
user@client:~$ python main.py client novpn -i/--iterations ITERATIONS [--auto]
```
Note, that it is necessary to give the iterations as input.

The `--auto` option lets the software save the hardware/network performance every 0.1 seconds automatically, additionally to the values when a new exchange starts. This makes sure that you get values during the entire exchange, without breaks in the execution stopping the values from being saved.

#### HTTP exchange via Rosenpass connection
Important: In exchanges with a high number of iterations you may be asked for your password multiple times. Enter your `sudo` password and the exchange will continue.

Start the HTTP exchange with Rosenpass VPN, by running the following commands:
```
user@server:~$ python main.py server rp [-i/--iterations ITERATIONS] [--auto]
```
```
user@client:~$ python main.py client rp [-i/--iterations ITERATIONS] [--auto]
```
Without setting the iterations, there will be as many exchanges as key sets in the corresponding folder. If you only created a single key beforehand, you can enter a number as `ITERATIONS` and the exchange will be repeated as often as you entered, using the same key.

The `--auto` option works as described in the baseline HTTP exchange above.

## Usage for Visualizing Data
### Generate correctly formatted data

To generate the data for later visualization, just follow the steps in the above chapter 'Usage for Performance Measurements'.

### Output graphs

To visualize the stored data, use
```
$ python DataOutput.py DIRECTORY|FILE [--compare COMPARE_NR]
```
where `DIRECTORY|FILE` is either the folder containing the `.json` files or the `.json` file itself. Note, that the format of each file has to be:
```
ROLE-VPN_OPTION:TIMESTAMP.json
```

`ROLE`: Role of the device (by default either `server` or `client`)

`VPN_OPTION`: VPN name (by default either `novpn` or `rp`)

`TIMESTAMP`: Timestamp, must be in ISO Format: `YYYY-MM-DD HH:MM:SS.mmmmmm`

`COMPARE_NR`: Number of graphs to compare (`1 < COMPARE_NR < 7`). When comparing graphs, it is only possible to compare the normal graphs, not the min/max/median graphs.

After executing the command, you will have to determine what graphs should be created. Here you can choose `all`, `cpu_percent`, `ram_percent`, `bytes_recv`, `bytes_sent`, `pps_recv` and `pps_sent`, or multiple of them by ticking the boxes.

You will also be asked if you want to generate the full relative graphs (0 to 100 percent) or only the part where values are present. You can also choose both.

You can also choose to create min/max/median graphs.