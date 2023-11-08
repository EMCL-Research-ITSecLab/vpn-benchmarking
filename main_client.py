from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":
	monitor = Monitoring()
	client = HTTPExchange.OnClient()
	monitor.start()
	### start test
	client.run(1000)
    ### end test
	monitor.stop()