from src.vpns.VPN import VPN


class NoVPN(VPN):
    """
    Implements the baseline without VPN. No VPN is used, therefore most methods just return a success.
    """

    def __init__(self, role) -> None:
        """
        :param role: role of the host
        """
        super().__init__(role)

    def open(self) -> bool:
        """
        Does not open a VPN.
        :return: returns True, since does not do anything
        """
        return True

    def close(self) -> bool:
        """
        Does not close any VPN.
        :return: returns True, since does not do anything
        """
        return True

    def generate_keys(self):
        """
        Does not need to generate keys, uses no keys.
        :return: returns True, since does not do anything
        """
        return True

    def share_pubkeys(self, remote_path) -> bool:
        """
        Does not send any keys, uses no keys.
        :return: returns True, since does not do anything
        """
        return True
