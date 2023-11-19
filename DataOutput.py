import json
import matplotlib.pyplot as plt
import sys


class DataOutput:
    l_cpu_percent = []
    l_ram_percent = []
    l_pps_sent = []
    l_bytes_sent = []
    
    def __init__(self, file_path) -> None:
        self.file = open(file_path)
        self.data = json.load(self.file)
    
    def make_graph(self,
        cpu_percent,
        ram_percent,
        pps_sent,
        bytes_sent
    ):
        for i in range(len(self.data["data"])):
            if cpu_percent == True: self.l_cpu_percent.append(self.__get_cpu_percent(i))
            if ram_percent == True: self.l_ram_percent.append(self.__get_ram_percent(i))
            if pps_sent == True: self.l_pps_sent.append(self.__get_pps_sent(i))
            if bytes_sent == True: self.l_bytes_sent.append(self.__get_bytes_sent(i))
        
        no_data = True
        if self.l_cpu_percent != []: no_data = False
        if self.l_ram_percent != []: no_data = False
        if self.l_pps_sent != []: no_data = False
        if self.l_bytes_sent != []: no_data = False
        
        if no_data:
            print("No data. Not saving a file.")
            return
        else:
            # TODO: Add way to plot multiple graphs into one graphic
            plt.plot(self.l_bytes_sent)
            plt.savefig("bytes_sent_c_rp")
            print("File saved as new.png.")
    
    def __get_cpu_percent(self, entry):
        return self.data["data"][entry]["hardware"][0]["cpu_percent"]
    
    def __get_ram_percent(self, entry):
        return self.data["data"][entry]["hardware"][0]["ram_percent"]
    
    def __get_pps_sent(self, entry):
        return self.data["data"][entry]["network"][0]["pps_sent"]
    
    def __get_bytes_sent(self, entry):
        return self.data["data"][entry]["network"][0]["bytes_sent"]
    

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: python3 DataOutput.py [file_path]")
    else:
        output = DataOutput(args[0])
        output.make_graph(
            cpu_percent=True,
            ram_percent=True,
            pps_sent=True,
            bytes_sent=True
        )
    