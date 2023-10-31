import http.client
import time


host_name = "localhost"
port = 8080


def connect_and_request():
	connection = http.client.HTTPConnection(host_name, port, timeout=10)
	
	connection.request("GET", "/")
	response = connection.getresponse()

	connection.close()


if __name__ == "__main__":
	for _ in range(1000):
		time.sleep(.1)
		connect_and_request()