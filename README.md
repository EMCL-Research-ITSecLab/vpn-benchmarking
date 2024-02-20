# VPN Benchmarking Framework

This project aims to measure and compare the performance overhead of using a VPN connection and to visualize the resulting data. The framework can be used for different tasks (like sending an HTTP GET packet or a big file) using different VPNs (like Wireguard or Rosenpass).

## Usage for Performance Measurements
### Installing libraries
As a first step, it is recommended to set up a virtual environment for the installation. For this, install `venv` on your machines and use
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
Alternatively, you can use the framework without a virtual environment. In that case, you will have to install the necessary modules yourself: `psutil`, `click`, `inquirer`, `numpy`, `pycurl`.

TODO: DELETE IF NOT NEEDED:

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
For setting up the environment if you want to measure the performance of Rosenpass, either install Rosenpass from their official GitHub page, or install Ansible on a third device (master), set up SSH keys on both hosts, copy the ansible hosts file from one of the hosts to master and use:
```
user@master:~/ansible_files$ ansible-playbook install_rosenpass.yml --ask-become-pass
```
You will be asked to enter the password for the remote machine. At the moment, it is only possible to update machines with the same password by running the command once.

If you want to test different VPNs, consider implementing the functionality as shown in the section of testing different VPNs.

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
with `VPN_OPTION` being the VPN you want to use (currently you can use `NoVPN` (baseline) and `Rosenpass`). `EXCHANGE_TYPE` describes what kind of exchange should be executed (currently you can use `HTTP` for sending a specified number of GET packets from the client to the server).

#### Sharing public keys with the other host
For sharing the keys, it is necessary to set up SSH keys on both the server and the client. To share the keys, execute:
```
user@server:~$ python main.py server VPN_OPTION EXCHANGE_TYPE keysend [-d REMOTE_CLIENT_DIRECTORY]
```
```
user@client:~$ python main.py client VPN_OPTION EXCHANGE_TYPE keysend [-d REMOTE_SERVER_DIRECTORY]
```
`REMOTE_SERVER_DIRECTORY` and `REMOTE_CLIENT_DIRECTORY` specify the working directory on the remote host, in which the folder `rp-keys` for the keys is existent (TODO: CHECK).

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
user@server:~$ python main.py server novpn http exchange -i/--iterations ITERATIONS [--auto]
```
```
user@client:~$ python main.py client novpn http exchange -i/--iterations ITERATIONS [--auto]
```
Note, that it is necessary to give the iterations as input.

The `--auto` option lets the software save the hardware/network performance every 0.1 seconds automatically, additionally to the values when a new exchange starts. This makes sure that you get values during the entire exchange, without breaks in the execution stopping the values from being saved.

#### HTTP exchange via Rosenpass connection
Important: In exchanges with a high number of iterations you may be asked for your password multiple times. Enter your `sudo` password and the exchange will continue.

Start the HTTP exchange with Rosenpass VPN, by running the following commands:
```
user@server:~$ python main.py server rosenpass http exchange -i/--iterations ITERATIONS [--auto]
```
```
user@client:~$ python main.py client rosenpass http exchange -i/--iterations ITERATIONS [--auto]
```
Enter a number as `ITERATIONS` and the exchange will be repeated as often as you entered, using the previously generated key set.

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

`VPN_OPTION`: VPN name (by default either `novpn` or `rosenpass`)

`TIMESTAMP`: Timestamp, must be in ISO Format: `YYYY-MM-DD HH:MM:SS.mmmmmm`

`COMPARE_NR`: Number of graphs to compare (`1 < COMPARE_NR < 7`). When comparing graphs, it is only possible to compare the normal graphs, not the min/max/median graphs.

After executing the command, you will have to determine what graphs should be created. Here you can choose `all`, `cpu_percent`, `ram_percent`, `bytes_recv`, `bytes_sent`, `pps_recv` and `pps_sent`, or multiple of them by ticking the boxes.

You will also be asked if you want to generate the full relative graphs (0 to 100 percent) or only the part where values are present. You can also choose both.

You can also choose to create min/max/median graphs.

## Using the framework with different VPNs/different exchange types

Currently, the framework provides the class `HTTP` in the `helpers/exchanges` directory for exchange types and the classes `NoVPN` and `Rosenpass` in the `helpers/vpns` directory for different VPNs.

To implement new VPNs or new exchanges, simply add new classes inheriting from the classes `VPN`/`Exchange` and implement their functions. Additionally, you will have to adjust the methods `__check_values` and `__create_instance` in the `HandleInput` class in `main.py`. Add the name of your added functionality and the corresponding creation of `Server`/`Client` by inputting your new class.