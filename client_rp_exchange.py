from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":
	monitor = Monitoring("client_rp_exchange")
	client = HTTPExchange.OnClient()

	monitor.start(auto=False)
	### start test
	client.run_with_rp(monitor=monitor)
    ### end test
	monitor.stop()