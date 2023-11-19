from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":        
    monitor = Monitoring()
    monitor_rp = Monitoring()
    server = HTTPExchange.OnServer()
    # server.gen_keys(5)
    # client.gen_keys(5)
    monitor.start(auto=False)
    ### start test
    # server.run(reps=5, monitor=None)
    server.run(5, monitor=monitor)

    #monitor_rp.start(auto=False)
    server.run_with_rp(monitor=monitor_rp)
    ### end test
    monitor.stop()
    monitor_rp.stop()