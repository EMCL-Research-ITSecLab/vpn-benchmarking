from helpers.vpns.VPN import VPN


class NoVPN(VPN):
    def __init__(self, role) -> None:
        super().__init__(role)

    def open(self) -> bool:
        # does not open any vpn
        return True

    def close(self) -> bool:
        # does not close any vpn
        return True

    def generate_keys(self):
        # no keys needed
        return True

    def share_pubkeys(self, remote_path) -> bool:
        # no keys needed
        return True
