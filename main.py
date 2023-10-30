#!/usr/bin/env python3

from Monitoring import Monitoring


# only for testing purposes     
def test():
    i = 0
    for _ in range(499999999):
        i += 1


if __name__ == "__main__":
    monitor = Monitoring()
    monitor.run(test)