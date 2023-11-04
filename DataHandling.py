import json
import datetime

### data is saved as
#{
#    "time": TODO, 
#    "cpu_percent": 22.4, 
#    "ram_percent": 34.1,
#	 "pps_sent": 1506,
#	 "pps_recv": 6,
#	 "bytes_sent": 13056,
#	 "bytes_recv": 5698
#} 


class DataHandling:
	data = { "data": [] }
 
	def __init__(self) -> None:
		self.timestamp = datetime.datetime.now()
  
	def write_data(self):
		with open(f"data/data:{self.timestamp}.json", "w") as file:
			json.dump(self.data, indent=2, sort_keys=True, fp=file)
        
	def add_data(self, 
        time, 
        cpu_perc, 
        ram_perc, 
        pps_sent, 
        pps_recv, 
        bytes_sent, 
        bytes_recv
    ):
		new_data = {
			"time": time, 
			"hardware": [
				{
					"cpu_percent": cpu_perc, 
   					"ram_percent": ram_perc
				}
			],
   			"network": [
				{
					"pps_sent": pps_sent,
					"pps_recv": pps_recv,
					"bytes_sent": bytes_sent,
					"bytes_recv": bytes_recv
				}
			]
		}
  
		self.data["data"].append(new_data)
  
dh = DataHandling()
dh.add_data(
    time="TODO", 
    cpu_perc=22.4, 
    ram_perc=34.1, 
    pps_sent=1506, 
    pps_recv=6, 
    bytes_sent=13056, 
    bytes_recv=5698)
dh.add_data(
    time="TODO", 
    cpu_perc=10.5, 
    ram_perc=36.9, 
    pps_sent=120, 
    pps_recv=2495, 
    bytes_sent=15078, 
    bytes_recv=7650)
dh.write_data()