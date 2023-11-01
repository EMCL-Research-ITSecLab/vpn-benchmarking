import http.client
import time


host_name = "localhost"
port = 8080


def run_test(reps):
	i = reps
	
	while i > 0:
		try:
			connection = http.client.HTTPConnection(host_name, port, timeout=10)
			
			connection.request("GET", "/")
			response = connection.getresponse()

			connection.close()
			i -= 1
		except:
			continue


if __name__ == "__main__":
	run_test(1000)