import json
import matplotlib.pyplot as plt
import os
from pathlib import Path


class DataOutput:
    lists = {
        "cpu_percent": [],
        "ram_percent": [],
        "pps_sent": [],
        "bytes_sent": []
    }
    
    def make_graphs_for_directory(self):
        # TODO: check if dir_path is a directory
        file_path = "data/client_rp_exchange_2023-11-19T13_23_40_608278.json"
        self.make_graphs_for_file(file_path)
        self.data = json.load(self.file)
    
    def make_graphs_for_file(self,
        file_path,
        cpu_percent=False,
        ram_percent=False,
        pps_sent=False,
        bytes_sent=False
    ):
        self.file = open("data/client_rp_exchange_2023-11-19T13_23_40_608278.json")
        self.data = json.load(self.file)
        # TODO: check if file_path is a file
        self.__make_graph(
            cpu_percent=cpu_percent,
            ram_percent=ram_percent,
            pps_sent=pps_sent,
            bytes_sent=bytes_sent
        )
    
    def __make_graph(self,
        cpu_percent,
        ram_percent,
        pps_sent,
        bytes_sent
    ):
        for i in range(len(self.data["data"])):
            if cpu_percent == True: self.lists["cpu_percent"].append(self.__get_cpu_percent(i))
            if ram_percent == True: self.lists["ram_percent"].append(self.__get_ram_percent(i))
            if pps_sent == True: self.lists["pps_sent"].append(self.__get_pps_sent(i))
            if bytes_sent == True: self.lists["bytes_sent"].append(self.__get_bytes_sent(i))
        
        # TODO: Add way to plot multiple graphs into one graphic
        no_data = True
        for l in self.lists:
            if self.lists[l] != []:
                short_path = f"data_graphs/test"
                file_path = os.path.join(os.getcwd(), short_path)
                Path(file_path).mkdir(parents=True, exist_ok=True)
                
                plt.plot(self.lists[l])
                plt.savefig(os.path.join(file_path, l))
                plt.clf()
                
                no_data = False
                print(f"File saved as {short_path}/{l}.png.")
        if no_data == True:
            print("No data. Not printing any graphs.")
    
    def __get_cpu_percent(self, entry):
        return self.data["data"][entry]["hardware"][0]["cpu_percent"]
    
    def __get_ram_percent(self, entry):
        return self.data["data"][entry]["hardware"][0]["ram_percent"]
    
    def __get_pps_sent(self, entry):
        return self.data["data"][entry]["network"][0]["pps_sent"]
    
    def __get_bytes_sent(self, entry):
        return self.data["data"][entry]["network"][0]["bytes_sent"]
    

if __name__ == "__main__":
    # args = sys.argv[1:]
    # if len(args) == 0:
    #     print("Usage: python3 DataOutput.py [file_path]")
    # else:
        output = DataOutput()
        output.make_graphs_for_file(
            file_path=None,
            cpu_percent=True,
            ram_percent=True,
            pps_sent=True,
            bytes_sent=True
        )
    