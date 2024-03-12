# VPN Benchmarking Framework

This project aims to measure and compare the performance overhead of using a VPN connection and to visualize the resulting data. The framework can be used for different tasks (like sending an HTTP GET packet or a big file) using different VPNs (like Wireguard or Rosenpass).

## Usage for Performance Measurements
### Installing libraries
To install the necessary dependencies, you can create a `venv` environment and use:
```
$ sudo python install_requirements.py
```

Alternatively, you can use the framework without a virtual environment. In that case, you will have to install the necessary modules yourself: `psutil`, `click`, `inquirer`, `numpy`, `pycurl`.

Set the device's role in the exchange by executing:
```
user@server:~$ sudo python set_role.py server
```
```
user@client:~$ sudo python set_role.py client
```

This will set up the needed folder structures.

### Setting the hosts
To define the host data, execute the command
```
$ python set_hosts.py --server USER@IP_ADDRESS --client USER@IP_ADDRESS
```
on all hosts.

`USER` and `IP_ADDRESS` describe the user and the IP address on the respective host.
Note, that both options `--server` and `--client` have to be set on both hosts.

After setting the hosts, you will be asked if you want to set the same hosts for the ansible hosts file. This can be used in the next step, to install Rosenpass on the hosts.

### Install latest Rosenpass version
For setting up the environment if you want to measure the performance of Rosenpass, either install Rosenpass from their official GitHub page, or use Ansible install Rosenpass on the remote host:
```
user@host:~/ansible_files$ ansible-playbook install_rosenpass.yml --ask-become-pass
```
You will be asked to enter the password for the remote machine.

### Generate keys and share public keys
All the following functions can be used by executing `main.py` with different arguments and options.

#### Generating keys
To generate the necessary keys, use the command:
```
user@server:~$ python main.py server VPN_OPTION EXCHANGE_TYPE keygen
```
```
user@client:~$ python main.py client VPN_OPTION EXCHANGE_TYPE keygen
```
with `VPN_OPTION` being the VPN you want to use (currently you can use `novpn` (baseline) and `rosenpass`). `EXCHANGE_TYPE` describes what kind of exchange should be executed (currently you can use `http` for sending a specified number of GET packets from the client to the server).

#### Sharing public keys with the other host
For sharing the keys, it is necessary to set up SSH keys on both the server and the client. To share the keys, execute:
```
user@server:~$ python main.py server VPN_OPTION EXCHANGE_TYPE keysend [-d REMOTE_CLIENT_DIRECTORY]
```
```
user@client:~$ python main.py client VPN_OPTION EXCHANGE_TYPE keysend [-d REMOTE_SERVER_DIRECTORY]
```
`REMOTE_SERVER_DIRECTORY` and `REMOTE_CLIENT_DIRECTORY` specify the working directory on the remote host, in which the folder `rp-keys` for the keys is existent.

### Execute HTTP exchange
Now the keys and hosts are ready to start and monitor exchanges. Start the server first.

#### HTTP exchange using no vpn (baseline)
Start the baseline HTTP exchange, by running the following commands:
```
user@server:~$ python main.py server novpn http exchange -i/--iterations ITERATIONS [--auto]
```
```
user@client:~$ python main.py client novpn http exchange -i/--iterations ITERATIONS [--auto]
```

The `--auto` option lets the software save the hardware/network performance every 0.1 seconds automatically, additionally to the values when a new exchange starts. This makes sure that you get values during the entire exchange, without breaks in the execution stopping the values from being saved.

#### HTTP exchange via Rosenpass connection
Start the HTTP exchange with Rosenpass VPN, by running the following commands:
```
user@server:~$ sudo python main.py server rosenpass http exchange -i/--iterations ITERATIONS [--auto]
```
```
user@client:~$ sudo python main.py client rosenpass http exchange -i/--iterations ITERATIONS [--auto]
```
Enter a number as `ITERATIONS` and the exchange will be repeated as often as you entered, using the previously generated key set.

The `--auto` option works as described in the baseline HTTP exchange above.

## Usage for Visualizing Data
### Generate correctly formatted data

To generate the data for later visualization, just follow the steps in the above chapter 'Usage for Performance Measurements'.

### Output diagrams

To visualize the stored data using graphs, use
```
$ python output.py OUTPUT_TYPE DIRECTORY|FILE [-d] [-f] [-n] [-m]
```
where `DIRECTORY|FILE` is either the folder containing the `.json` files or the `.json` file itself, and `OUTPUT_TYPE` is the type of diagram to be created. The base version of the framework can create graphs (for this, set `OUTPUT_TYPE` to `graphs`).

At least one of the flags `-d` (detailed) `-f` (full) has to be set, this also applies to the flags `-n` (normal) and `-m` (min/max/median).  A detailed graph only shows the range on relative graphs where values are present, a full graph shows the entire range from 0 to 100 percent. A normal graph displays all values, while a min/max/median graph splits the data into 8 intervals, and shows the value range as well as the median.

After executing the command, you will have to determine what graphs should be created. Here you can choose the value types you want to generate graphs for.

## Expanding the framework

Currently, the framework provides the class `HTTP` in the `helpers/exchanges` directory for exchange types and the classes `NoVPN` and `Rosenpass` in the `helpers/vpns` directory for different VPNs. You can implement new classes to extend the base exchange types and VPNs.