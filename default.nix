# default.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.callPackage ./vpn-benchmarking.nix {}