from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":        
    monitor = Monitoring()
    server = HTTPExchange.OnServer()
    monitor.start(auto=False)
    ### start test
    server.run(reps=1000, monitor=monitor)
    ### end test
    monitor.stop()