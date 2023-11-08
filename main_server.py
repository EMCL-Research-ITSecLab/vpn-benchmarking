from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":        
    monitor = Monitoring()
    server = HTTPExchange.OnServer()
    monitor.start()
    ### start test
    server.run(1000)
    ### end test
    monitor.stop()