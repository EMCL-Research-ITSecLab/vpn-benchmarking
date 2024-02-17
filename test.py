from Monitoring import Monitoring
from new_version.Server import *
from new_version.exchanges.HTTP import *
from new_version.vpns.NoVPN import *

monitor = Monitoring("test", "novpn")
server = Server(HTTP, NoVPN)

def test1():
    for i in range(99999):
        i += 1
        print(i)


monitor.start(auto=True)
### start test
server.run(1)
### end test
monitor.stop()
