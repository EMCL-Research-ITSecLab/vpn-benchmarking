from new_version.Server import Server
from new_version.Client import Client
from new_version.Exchange import Exchange
from new_version.VPN import VPN
from new_version.exchanges.HTTP import HTTP
from new_version.vpns.NoVPN import NoVPN
from new_version.vpns.Rosenpass import Rosenpass

rosenpass = Rosenpass("server", "localhost", "lamron")

rosenpass.generate_keys(10)
