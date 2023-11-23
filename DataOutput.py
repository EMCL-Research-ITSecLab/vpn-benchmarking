import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
from pathlib import Path
import sys
from datetime import datetime
from error_messages import print_err
from error_messages import print_warn


class DataOutput:
    lists = {
        "time": [],
        "cpu_percent": [],
        "ram_percent": [],
        "bytes_recv": [],
        "bytes_sent": [],
        "pps_recv": [],
        "pps_sent": []
    }
    
    def make_graphs_for_directory(self, 
        dir_path,
        cpu_percent=False,
        ram_percent=False,
        bytes_recv=False,
        bytes_sent=False,
        pps_recv=False,
        pps_sent=False
    ):
        try:
            for file in os.listdir(dir_path):
                if file[-5:] == ".json":
                    file_path = dir_path + "/" + file
                    self.make_graphs_for_file(
                        file_path,
                        cpu_percent=cpu_percent,
                        ram_percent=ram_percent,
                        bytes_recv=bytes_recv,
                        bytes_sent=bytes_sent,
                        pps_recv=pps_recv,
                        pps_sent=pps_sent
                    )
                    plt.close()
        except NotADirectoryError:
            print_err("The given path is not a directory!")
    
    def make_graphs_for_file(self,
        file_path,
        cpu_percent=False,
        ram_percent=False,
        bytes_recv=False,
        bytes_sent=False,
        pps_recv=False,
        pps_sent=False
    ):
        self.file = open(file_path)
        self.data = json.load(self.file)
        file_name = os.path.basename(file_path)
        
        if file_name[-5:] != ".json":
            print_warn(f"Skipping {file_name}. Not a json file!")
            return
        
        self.__make_graph(
            file_name=file_name,
            cpu_percent=cpu_percent,
            ram_percent=ram_percent,
            bytes_recv=bytes_recv,
            bytes_sent=bytes_sent,
            pps_recv=pps_recv,
            pps_sent=pps_sent
        )
    
    def __make_graph(self,
        file_name,
        cpu_percent,
        ram_percent,
        bytes_recv,
        bytes_sent,
        pps_recv,
        pps_sent
    ):
        self.__reset_lists()
        
        for i in range(len(self.data["data"])):
            self.lists["time"].append(self.__get_time_stamp(i))
            if cpu_percent == True: self.lists["cpu_percent"].append(self.__get_cpu_percent(i))
            if ram_percent == True: self.lists["ram_percent"].append(self.__get_ram_percent(i))
            if bytes_recv == True: self.lists["bytes_recv"].append(self.__get_bytes_recv(i))
            if bytes_sent == True: self.lists["bytes_sent"].append(self.__get_bytes_sent(i))
            if pps_recv == True: self.lists["pps_recv"].append(self.__get_pps_recv(i))
            if pps_sent == True: self.lists["pps_sent"].append(self.__get_pps_sent(i))
        
        # get the times as difference from the initial time
        time_stamps = [0]
        initial_time = datetime.fromisoformat(self.lists["time"][0])
        for i in range(1, len(self.lists["time"])):
            cur_time = datetime.fromisoformat(self.lists["time"][i])
            time_stamps.append((cur_time - initial_time).total_seconds())
        
        # TODO: Add way to plot multiple graphs into one graphic
        no_data = True
        for l in self.lists:
            if self.lists[l] != [] and l != "time":
                short_path = f"data_graphs/{file_name[:-5]}"
                file_path = os.path.join(os.getcwd(), short_path)
                Path(file_path).mkdir(parents=True, exist_ok=True)
                
                plt.grid(True, 'both', 'y')
                plt.xlabel("time [s]")
                
                if l == "bytes_recv" or l == "bytes_sent":
                    # get the unit of the maximum value and use it for all values
                    values = self.lists[l]
                    unit = self.__get_unit(max(values))
                    
                    while max(values) > 1024:
                        for v in range(len(values)):
                            values[v] = values[v] / 1024
                    
                    plt.ylabel(f"{l} [{unit}]")
                    
                    plt.xlim([0, max(time_stamps)])
                    plt.ylim([0, max(values) + 0.05 * max(values)])
                    
                    plt.plot(time_stamps, values)
                elif l == "cpu_percent" or l == "ram_percent":
                    plt.ylabel(f"{l} [%]")
                    
                    plt.xlim([0, max(time_stamps)])
                    plt.ylim([0, 100])
                    
                    plt.plot(time_stamps, self.lists[l])
                else:
                    plt.plot(time_stamps, self.lists[l])
                
                plt.savefig(os.path.join(file_path, l))
                plt.clf()
                
                no_data = False
                print(f"File saved as {short_path}/{l}.png.")
        if no_data == True:
            print("No data. Not printing any graphs.")
        
        # reset data lists
        self.__reset_lists()
    
    def __reset_lists(self):
        for l in self.lists:
            self.lists[l] = []
            
    def __get_unit(self, bytes):
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                if unit == '':
                    return "B"
                else:
                    return f"{unit}iB"
            bytes = bytes / 1024
        print_err("Number of bytes is too large!")

    def __get_time_stamp(self, entry):
        return self.data["data"][entry]["time"]

    def __get_cpu_percent(self, entry):
        return self.data["data"][entry]["hardware"][0]["cpu_percent"]
    
    def __get_ram_percent(self, entry):
        return self.data["data"][entry]["hardware"][0]["ram_percent"]
    
    def __get_bytes_recv(self, entry):
        return self.data["data"][entry]["network"][0]["bytes_recv"]
    
    def __get_bytes_sent(self, entry):
        return self.data["data"][entry]["network"][0]["bytes_sent"]
    
    def __get_pps_recv(self, entry):
        return self.data["data"][entry]["network"][0]["pps_recv"]
    
    def __get_pps_sent(self, entry):
        return self.data["data"][entry]["network"][0]["pps_sent"]

if __name__ == "__main__":
    # args = sys.argv[1:]
    # if len(args) == 0:
    #     print("Usage: python3 DataOutput.py [file_path/dir_path]")
    # elif len(args) == 1:
        path = "data" # args[0]
        # if path is directory
        if os.path.isdir(path):
            output = DataOutput()
            print("Creating graphs for all json files in the directory...")
            output.make_graphs_for_directory(
                dir_path=path,
                cpu_percent=True,
                ram_percent=True,
                bytes_recv=True,
                bytes_sent=True,
                pps_recv=True,
                pps_sent=True
            )
        # if path is json file
        elif os.path.isfile(path) and path[-5:] == ".json":
            output = DataOutput()
            print("Creating graphs for the file...")
            output.make_graphs_for_file(
                file_path=path,
                cpu_percent=True,
                ram_percent=True,
                bytes_recv=True,
                bytes_sent=True,
                pps_recv=True,
                pps_sent=True
            )
        # if path other file
        elif os.path.exists(path):
            print_err("The given file is not a json file.")
        # path does not exist
        else:
            print_err("The given path does not exist.")
    # else:   # more than one argument
    #     # TODO
    #     pass
    