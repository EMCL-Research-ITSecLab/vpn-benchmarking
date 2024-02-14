from new_version.VPN import VPN

import messages


class NoVPN(VPN):
    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        super().__init__(role, remote_ip_addr, remote_user)

    def open(self) -> bool:
        # does not open any vpn
        return True

    def close(self) -> bool:
        # does not close any vpn
        return True

    def share_pubkeys(self, remote_path) -> bool:
        # no keys needed
        return True
