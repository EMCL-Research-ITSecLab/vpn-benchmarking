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

    def generate_keys(self, number):
        # no keys needed
        return True

    def count_keys(self) -> int:
        # no keys to count
        return 0  # TODO: Check if return 0 or return -1

    def share_pubkeys(self, remote_path) -> bool:
        # no keys needed
        return True
