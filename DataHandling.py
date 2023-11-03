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
	def __init__(self) -> None:
		self.timestamp = datetime.datetime.now()
		self.file = open(f"data/data:{self.timestamp}.json", "w")
        
    # save the data to the json file
	def save_data(self, 
        time, 
        cpu_perc, 
        ram_perc, 
        pps_sent, 
        pps_recv, 
        bytes_sent, 
        bytes_recv
    ):
		data = {
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
  
		#self.file_data["data"].append(data)
		self.file.write(json.dumps(data, indent=4, sort_keys=True))
  
dh = DataHandling()
dh.save_data(
    time="TODO", 
    cpu_perc=22.4, 
    ram_perc=34.1, 
    pps_sent=1506, 
    pps_recv=6, 
    bytes_sent=13056, 
    bytes_recv=5698)