from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":
    monitor = Monitoring("client_novpn_exchange")
    client = HTTPExchange.OnClient()

    monitor.start(auto=False)
    ### start test
    client.run(100, monitor=monitor)
    ### end test
    monitor.stop()
