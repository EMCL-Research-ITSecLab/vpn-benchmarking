# Rosenpass Benchmarking

This project aims to measure and compare the performance overhead of using a post-quantum-secure Rosenpass VPN connection and to visualize the resulting data.

## Usage
### Installing libraries
As a first step, you need to install necessary libraries by executing:
```
python install_requirements.py server|client
```
where the argument `server` or `client` determines what role the current host gets. It is important to keep that role from now on.

### Setting the hosts
Next, you need to set the hosts that take part in the exchange. For this, execute the command:
```
python set_hosts.py --server USER@IP_ADDRESS:PORT --client USER@IP_ADDRESS
```
`USER` and `IP_ADDRESS` describe the user and the IP address on the respective host, the port for opening the server needs to be specified as `PORT` in the server option.
Note, that both options `--server` and `--client` have to be set on both hosts.

After setting the hosts, you will be asked if you want to set the same hosts for the ansible hosts file. This can be used in the next step, to install Rosenpass on the hosts. Confirm if you need to install or update Rosenpass.

### Install latest Rosenpass version
For setting up the environment, install Ansible on a third device (master host) and use:
```
ansible-playbook install_rosenpass.yml --ask-become-pass
```
You will be asked to enter the password for the remote machine. At the moment, it is only possible to update machines with the same password by running the command once.

### Generate Rosenpass keys and share public keys
All the following functions can be used by executing `main.py` with different arguments and options.

#### Generating Rosenpass keys
To generate the necessary keys, use the command:
```
python main.py server|client keygen [-i/--iterations ITERATIONS]
```
with `ITERATIONS` being the number of key sets that need to be generated. By default, this value is 1. By specifying the number of keys manually, you can create several different Rosenpass key sets. In the exchange, every connection will use a different key set. By setting the number to 1 (default), only one key will be generated and used in the exchange. The number of iterations can then be specified later when executing the exchange.

As mentioned earlier, the argument `server|client` must match the argument used in the first step.

#### Sharing Rosenpass public keys with the other host
For sharing the keys, it is necessary to set up SSH keys on both the server and the client.

### Execute HTTP Exchange

#### HTTP Exchange using no vpn (baseline)

#### HTTP Exchange via Rosenpass connection