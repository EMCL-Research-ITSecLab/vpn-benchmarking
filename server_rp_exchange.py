from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":        
    monitor = Monitoring("server_rp_exchange")
    server = HTTPExchange.OnServer()

    monitor.start(auto=False)
    ### start test
    server.run_with_rp(monitor=monitor)
    ### end test
    monitor.stop()