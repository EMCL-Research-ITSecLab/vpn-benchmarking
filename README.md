# rosenpass-benchmarking

This project aims to measure and compare the performance overhead of using a post-quantum-secure Rosenpass VPN connection and to visualize the resulting data.

For setting up the environment, you can use ansible files:
For usage, the working directory must include a file `hosts` with the following content:
```
[server_name] ansible_host=[server_ip] ansible_user=[server_user]
[client_name] ansible_host=[client_ip] ansible_user=[client_user]
```

To install Rosenpass on the remote hosts, execute the following command:
```
ansible-playbook install_rosenpass.yml --ask-become-pass
```
You will be asked to enter the password for the remote machine. At the moment, it is only possible to update machines with the same password by running the command once.

To generate and copy the necessary Rosenpass keys on and to all the hosts, run the command:
```
ansible-playbook generate_and_send_rp_keys.yml
```