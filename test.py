import os
import subprocess


path = os.path.join(os.getcwd(), "rp-exchange/rp-keys/client-public-1")
count = 0
            
for p in os.listdir(path):
    count += 1
                    
print('File count:', count)

#   rp-exchange
#       rp-keys
#           000001_server.rosenpass-public
#           000001_server.rosenpass-secret
#           000002_server.rosenpass-public
#           000002_server.rosenpass-secret
#           ...
#           500000_server.rosenpass-public
#           500000_server.rosenpass-secret


# subprocess.run(["scp", FILE, "USER@SERVER:PATH"])
