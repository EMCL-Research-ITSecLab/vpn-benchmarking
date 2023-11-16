from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":        
    monitor = Monitoring("novpn-exchange")
    # TODO: Test with new folder nopvn-exchange
    server = HTTPExchange.OnServer()
    monitor.start(auto=True)
    ### start test
    server.run(reps=1000, monitor=monitor)
    # server.run_with_rp(None)
    ### end test
    monitor.stop()