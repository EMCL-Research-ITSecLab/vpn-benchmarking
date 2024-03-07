from io import BytesIO

import pycurl

buffer = BytesIO()
url = f"http://192.168.2.227:80"
c = pycurl.Curl()
c.setopt(pycurl.URL, url)
c.setopt(pycurl.HTTPGET, True)

# if the VPN uses a different interface, get its name
# c.setopt(pycurl.INTERFACE, "eth0")

c.setopt(pycurl.TIMEOUT, 10)
c.setopt(pycurl.WRITEDATA, buffer)

try:
     c.perform()
     response_code = c.getinfo(pycurl.RESPONSE_CODE)
     c.close()

     if response_code == 200:
         print("Request successful!")
except:
    print("Nope")
    pass