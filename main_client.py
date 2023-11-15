from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":
	monitor = Monitoring("novpn-exchange")
	client = HTTPExchange.OnClient()
	monitor.start(auto=False)
	### start test
	client.run(reps=1000, monitor=monitor)
    ### end test
	monitor.stop()