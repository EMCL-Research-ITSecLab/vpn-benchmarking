import json
import datetime
from pathlib import Path


class DataHandling:
	data = { "data": [] }
 
	def __init__(self) -> None:
		self.timestamp = datetime.datetime.now()
		Path("data").mkdir(parents=True, exist_ok=True)
  
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
  