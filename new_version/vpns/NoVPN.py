from new_version.VPN import VPN

import messages


class NoVPN(VPN):
    def __init__(self, role) -> None:
        super().__init__(role)

    def open(self) -> bool:
        # does not open any vpn
        return True

    def close(self) -> bool:
        # does not close any vpn
        return True

    def share_pubkeys(self) -> bool:
        # no keys needed
        return True
