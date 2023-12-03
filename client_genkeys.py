from HTTPExchange import HTTPExchange


if __name__ == "__main__":
    client = HTTPExchange.OnClient()
    client.gen_keys(100)
