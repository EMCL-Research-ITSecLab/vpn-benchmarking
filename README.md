# Rosenpass Benchmarking

This project aims to measure and compare the performance overhead of using a post-quantum-secure Rosenpass VPN connection and to visualize the resulting data.

## Usage
### Installing libraries
As a first step, you need to install necessary libraries by executing:
```
user@server:~$ python install_requirements.py server
```
```
user@client:~$ python install_requirements.py client
```
where the argument `server` or `client` determines what role the current host gets. It is important to keep that role from now on.

### Setting the hosts
Next, you need to set the hosts that take part in the exchange. For this, execute the command:
```
$ python set_hosts.py --server USER@IP_ADDRESS:PORT --client USER@IP_ADDRESS
```
`USER` and `IP_ADDRESS` describe the user and the IP address on the respective host, the port for opening the server needs to be specified as `PORT` in the server option.
Note, that both options `--server` and `--client` have to be set on both hosts.

After setting the hosts, you will be asked if you want to set the same hosts for the ansible hosts file. This can be used in the next step, to install Rosenpass on the hosts. Confirm if you need to install or update Rosenpass.

### Install latest Rosenpass version
For setting up the environment, install Ansible on a third device (master), set up SSH keys on both hosts and use:
```
user@master:~$ ansible-playbook install_rosenpass.yml --ask-become-pass
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
user@server:~$ python main.py server keysend -d [REMOTE_CLIENT_DIRECTORY]
```
```
user@client:~$ python main.py client keysend -d [REMOTE_SERVER_DIRECTORY]
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
user@server:~$ python main.py server rp 
```

#### HTTP exchange via Rosenpass connection