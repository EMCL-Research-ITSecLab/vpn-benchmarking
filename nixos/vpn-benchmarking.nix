# vpn-benchmarking.nix
{ fetchFromGitHub
, pkgs ? import <nixpkgs> { }
,
}:

pkgs.stdenv.mkDerivation {
  name = "vpnbenchmarking";
  version = "1.0.0";
  src = fetchFromGitHub {
    owner = "EMCL-Research-ITSecLab";
    repo = "vpn-benchmarking";
    rev = "773145e";
    sha256 = "...";
  };

  propagatedBuildInputs = [
    pkgs.python3
    pkgs.virtualenv
  ];

  installPhase = ''
    mkdir -p $out
    cp -r  $src/src/ $out/
    cp -r  $src/main.py $out/
    cp -r  $src/set_hosts.py $out/
    cp -r  $src/requirements.txt $out/

    ${pkgs.python3.interpreter} -m venv "$out/.venv"
  '';
}