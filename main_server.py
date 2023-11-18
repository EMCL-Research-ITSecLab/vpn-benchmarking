from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":        
    # monitor = Monitoring()
    server = HTTPExchange.OnServer()
    # client = HTTPExchange.OnClient()
    # server.gen_keys(5)
    # client.gen_keys(5)
    # monitor.start(auto=True)
    ### start test
    # server.run(reps=1000, monitor=monitor)
    server.run_with_rp(monitor=None)
    ### end test
    # monitor.stop()