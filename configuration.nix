{ config, pkgs, ... }:

{
  imports = [ <nixpkgs/nixos/modules/installer/virtualbox-demo.nix> ];

environment.systemPackages = [
	pkgs.xfce.mousepad
	pkgs.python3
	pkgs.wireguard-tools
	pkgs.openvpn
	pkgs.openssh
	pkgs.virtualenv
	pkgs.easyrsa
];

# Enable the OpenSSH daemon.
services.openssh.enable = true;

networking.firewall = {
  	allowedTCPPorts = [ 80 ];
  	allowedUDPPorts = [ 1194 ];
};

}
