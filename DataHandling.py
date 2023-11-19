import json
import datetime
from pathlib import Path
from json import JSONEncoder


class DataHandling:
	data = { "data": [] }
 
	def __init__(self, name) -> None:
		self.timestamp = datetime.datetime.now().isoformat()
  	self.name = name
		Path("data").mkdir(parents=True, exist_ok=True)
  
	def write_data(self):
		with open(f"data/{self.name}:{self.timestamp}.json", "w") as file:
			json.dump(self.data, indent=2, sort_keys=True, fp=file, cls=DateTimeEncoder)
        
	def add_data(self, 
        name,
        time, 
        cpu_perc, 
        ram_perc, 
        pps_sent, 
        pps_recv, 
        bytes_sent, 
        bytes_recv
    ):
		new_data = {
			"name": name,
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
  
  
class DateTimeEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
  