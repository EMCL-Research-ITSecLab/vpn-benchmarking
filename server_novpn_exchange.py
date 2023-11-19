from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":        
    monitor = Monitoring("server_novpn_exchange")
    server = HTTPExchange.OnServer()

    monitor.start(auto=False)
    ### start test
    server.run(100, monitor=monitor)
    ### end test
    monitor.stop()