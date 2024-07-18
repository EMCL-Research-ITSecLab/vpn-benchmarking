# vpn-benchmarking.nix
{
  stdenv,
  fetchFromGitHub,
  pkgs ? import <nixpkgs> {},
}:



stdenv.mkDerivation {
  pname = "mysoftware";
  version = "1.0.0";  src = fetchFromGitHub {
    owner = "EMCL-Research-ITSecLab";
    repo = "vpn-benchmarking";
    rev = "bf27feb";
    sha256 = "sha256-zZGqUVDyyAW1VEZGz/OOh5qzhPGPv26iogmN9mZnvZ8=";
  };


  installPhase = ''
   mkdir -p $out
   cp -r $src/* $out/
  '';
}
