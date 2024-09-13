 { config, pkgs, lib, ... }:

{
  imports = [
    <nixos/nixos/modules/installer/sd-card/sd-image-aarch64.nix>
  ];

  # NixOS wants to enable GRUB by default
  boot.loader.grub.enable = false;

	system.copySystemConfiguration = true;

  # Enables the generation of /boot/extlinux/extlinux.conf
  boot.loader.generic-extlinux-compatible.enable = true;

  # !!! Set to specific linux kernel version
  boot.kernelPackages = pkgs.linuxPackages;

  # Disable ZFS on kernel 6
  boot.supportedFilesystems = lib.mkForce [
    "vfat"
    "xfs"
    "cifs"
    "ntfs"
  ];

  # !!! Needed for the virtual console to work on the RPi 3, as the default of 16M doesn't seem to be enough.
  # If X.org behaves weirdly (I only saw the cursor) then try increasing this to 256M.
  # On a Raspberry Pi 4 with 4 GB, you should either disable this parameter or increase to at least 64M if you want the USB ports to work.
  boot.kernelParams = [ "cma=256M" ];

  # File systems configuration for using the installer's partition layout
  fileSystems = {
    # Prior to 19.09, the boot partition was hosted on the smaller first partition
    # Starting with 19.09, the /boot folder is on the main bigger partition.
    # The following is to be used only with older images.
    /*
      "/boot" = {
      device = "/dev/disk/by-label/NIXOS_BOOT";
      fsType = "vfat";
      };
    */
    "/" = {
      device = "/dev/disk/by-label/NIXOS_SD";
      fsType = "ext4";
    };
  };

  # !!! Adding a swap file is optional, but strongly recommended!
  swapDevices = [{ device = "/swapfile"; size = 1024; }];

  # Settings above are the bare minimum
  # All settings below are customized depending on your needs

  environment.systemPackages = with pkgs; [
    vim
    curl
    wget
    nano
    bind
    xfce.mousepad
    python3
    wireguard-tools
    openvpn
    openssh
    virtualenv
    easyrsa
    (callPackage ./vpn-benchmarking.nix { })
  ];
  # Do not compress the image as we want to use it straight away
  sdImage.compressImage = false;

  # Enable the OpenSSH daemon.
  services.openssh = {
    enable = true;
    settings.PermitRootLogin = "yes";
  };

  users.mutableUsers = true;
  users.groups = {
    nixos = {
      gid = 1000;
      name = "nixos";
    };
  };
  users.users = {
    nixos = {
      uid = 1000;
      home = "/home/nixos";
      name = "nixos";
      group = "nixos";
      shell = pkgs.bash;
			isNormalUser  = true;
			initialPassword = "...";
      extraGroups = [ "wheel" "docker" ];
    };
  };
  users.users.root.openssh.authorizedKeys.keys = [
    # Your ssh key
    "..."
  ];

  networking.firewall = {
    allowedTCPPorts = [ 80 1194 ];
    allowedUDPPorts = [ 1194 51820 ];
  };

  system.stateVersion = "24.05";
}