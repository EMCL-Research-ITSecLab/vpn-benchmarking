from Monitoring import Monitoring
from HTTPExchange import HTTPExchange


if __name__ == "__main__":
    server = HTTPExchange.OnServer()
    server.gen_keys(100)
