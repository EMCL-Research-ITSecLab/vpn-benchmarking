import messages


class VPN:
    def __init__(self, role, remote_ip_addr, remote_user) -> None:
        self.role = None
        self.remote_ip_addr = remote_ip_addr
        self.remote_user = remote_user

        if role not in ("server", "client"):
            messages.print_err(
                "Unable to open VPN connection: unknown role. Known: server, client"
            )
            return
        else:
            self.role = role
            return

    def open(self) -> bool:
        messages.print_err("VPN.open(self): NOT IMPLEMENTED")
        return False

    def close(self) -> bool:
        messages.print_err("VPN.close(self): NOT IMPLEMENTED")
        return False

    def share_pubkeys(self, remote_path) -> bool:
        messages.print_err("VPN.share_pubkeys(self, remote_path): NOT IMPLEMENTED")
        return False
