from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":
	monitor = Monitoring()
	client = HTTPExchange.OnClient()
	monitor.start(auto=False)
	### start test
	client.run(reps=5, monitor=monitor)

	client.run_with_rp(monitor=monitor)
    ### end test
	monitor.stop()