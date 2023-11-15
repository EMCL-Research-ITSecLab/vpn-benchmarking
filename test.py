import os
import subprocess

print(f"Generating {8} rosenpass and wireguard keys...")
iterations = 5

home_path = os.getcwd()
os.makedirs(os.path.join(home_path, "rp-exchange/rp-keys"), exist_ok=True)

for i in range(iterations):
    formatted_number = '{num:0>{len}}'.format(num=i, len=len(str(iterations)))
    os.system(f"rp genkey rp-exchange/rp-keys/tmp/{formatted_number}_server.rosenpass-secret")

#   rp-exchange
#       rp-keys
#           000001_server.rosenpass-public
#           000001_server.rosenpass-secret
#           000002_server.rosenpass-public
#           000002_server.rosenpass-secret
#           ...
#           500000_server.rosenpass-public
#           500000_server.rosenpass-secret

number = 100
print()


# subprocess.run(["scp", FILE, "USER@SERVER:PATH"])
