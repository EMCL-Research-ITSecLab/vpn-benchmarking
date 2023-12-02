import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
from pathlib import Path
from datetime import datetime
from error_messages import print_err
from error_messages import print_warn
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import click
import inquirer


class DataOutput:
    lists = {
        "time": [],
        "cpu_percent": [],
        "ram_percent": [],
        "bytes_recv": [],
        "bytes_sent": [],
        "pps_recv": [],
        "pps_sent": [],
    }

    def __init__(
        self,
        cpu_percent=True,
        ram_percent=True,
        bytes_recv=True,
        bytes_sent=True,
        pps_recv=True,
        pps_sent=True,
    ) -> None:
        self.cpu_percent = cpu_percent
        self.ram_percent = ram_percent
        self.bytes_recv = bytes_recv
        self.bytes_sent = bytes_sent
        self.pps_recv = pps_recv
        self.pps_sent = pps_sent

    def make_graphs_for_directory(self, dir_path):
        try:
            for file in os.listdir(dir_path):
                if file[-5:] == ".json":
                    file_path = dir_path + "/" + file
                    self.make_graphs_for_file(file_path)
                    plt.close()
        except NotADirectoryError:
            print_err("The given path is not a directory!")

    def make_graphs_for_file(self, file_path):
        self.file = open(file_path)
        self.data = json.load(self.file)
        file_name = os.path.basename(file_path)

        if file_name[-5:] != ".json":
            print_warn(f"Skipping {file_name}. Not a json file!")
            return

        self.__make_graph(file_name)

    def compare_graphs(self, path, number_of_files):
        # check if the number of files is too high
        max_number_of_files = 6
        if number_of_files < 2 or number_of_files > max_number_of_files:
            print_err(
                f"Number of files too large! You can enter between 2 and {max_number_of_files} files."
            )
            return

        # initialize lists for the file paths and the names for the graphs
        files = []
        names = []

        # change to the directory given as input
        try:
            os.chdir(path)
        except:
            print_err("The given path was not found.")
            return

        # ask for the file paths and the names for the graphs
        for i in range(1, number_of_files + 1):
            file_path = prompt(f"File {i} path: ", completer=PathCompleter())
            files.append(file_path)
            name = prompt("Enter a name: ")
            names.append(name)

        self.__reset_lists()
        max_bytes_recv = 0
        max_bytes_sent = 0
        
        for l in self.lists:
            # skip this iteration for all values that we will not compute a graph for
            if l == "time":
                continue
            elif l == "cpu_percent" and self.cpu_percent == False:
                continue
            elif l == "ram_percent" and self.ram_percent == False:
                continue
            elif l == "bytes_recv" and self.bytes_recv == False:
                continue
            elif l == "bytes_sent" and self.bytes_sent == False:
                continue
            elif l == "pps_recv" and self.pps_recv == False:
                continue
            elif l == "pps_sent" and self.pps_sent == False:
                continue

            for f in files:
                # open the corresponding file for the file path and the currently looked at value
                self.file = open(f)
                file_name = os.path.basename(f)

                # check if the file is a json file
                if file_name[-5:] != ".json":
                    print_err(
                        f"At least one file was not a json file. Please try again."
                    )
                    return

                self.data = json.load(self.file)

                # compute the maximum value for the bytes (needed for correct bounds on the graphs)
                for i in range(len(self.data["data"])):
                    cur_b_recv = self.__get_bytes_recv(i)
                    cur_b_sent = self.__get_bytes_sent(i)
                    if cur_b_recv > max_bytes_recv:
                        max_bytes_recv = cur_b_recv
                    if cur_b_sent > max_bytes_sent:
                        max_bytes_sent = cur_b_sent

            short_path = ""
            full_path = ""

            data_exists = False
            for f in range(len(files)):
                # load the file
                self.file = open(files[f])
                file_name = os.path.basename(files[f])
                self.data = json.load(self.file)

                # get the timestamps from the file
                if self.lists["time"] == []:
                    for i in range(len(self.data["data"])):
                        self.lists["time"].append(self.__get_time_stamp(i))

                # append all values that we want a graph for
                for i in range(len(self.data["data"])):
                    if l == "cpu_percent":
                        self.lists["cpu_percent"].append(self.__get_cpu_percent(i))
                    if l == "ram_percent":
                        self.lists["ram_percent"].append(self.__get_ram_percent(i))
                    if l == "bytes_recv":
                        self.lists["bytes_recv"].append(self.__get_bytes_recv(i))
                    if l == "bytes_sent":
                        self.lists["bytes_sent"].append(self.__get_bytes_sent(i))
                    if l == "pps_recv":
                        self.lists["pps_recv"].append(self.__get_pps_recv(i))
                    if l == "pps_sent":
                        self.lists["pps_sent"].append(self.__get_pps_sent(i))

                # calculate the relative values of the timestamps (0 to 100 percent)
                timestamps = self.__get_relative_timestamps()

                # get the file paths and create directory if needed
                short_path = f"data_graphs/comparison"
                full_path = os.path.join(os.getcwd(), short_path)

                if self.lists[l] != [] and l != "time":     	# make sure the file contains data that is not timestamps
                    data_exists = True
                    Path(full_path).mkdir(parents=True, exist_ok=True)

                    # basic plot settings
                    plt.grid(True, "both", "y")
                    plt.xlabel(f"time [% of full exchange]")
                    plt.minorticks_on()

                    if l == "bytes_recv":
                        values = self.lists[l]

                        unit = self.__get_unit(max_bytes_recv)
                        plt.ylabel(f"total bytes (received) [{unit}]")

                        tmp_max = max_bytes_recv
                        while tmp_max > 1024:
                            for v in range(len(values)):
                                values[v] = values[v] / 1024
                            tmp_max = tmp_max / 1024

                        plt.xlim([0, 100])
                        plt.ylim([0, tmp_max + 0.05 * tmp_max])

                        plt.plot(timestamps, values, label=names[f])
                    elif l == "bytes_sent":
                        values = self.lists[l]

                        unit = self.__get_unit(max_bytes_sent)
                        plt.ylabel(f"total bytes (sent) [{unit}]")

                        tmp_max = max_bytes_sent
                        while tmp_max > 1024:
                            for v in range(len(values)):
                                values[v] = values[v] / 1024
                            tmp_max = tmp_max / 1024

                        plt.xlim([0, 100])
                        plt.ylim([0, tmp_max + 0.05 * tmp_max])

                        plt.plot(timestamps, values, label=names[f])
                    elif l == "cpu_percent" or l == "ram_percent":
                        if l == "cpu_percent":
                            plt.ylabel("CPU usage [%]")
                        else:
                            plt.ylabel("RAM usage [%]")

                        plt.xlim([0, 100])
                        plt.ylim([0, 100])
                        plt.yticks(ticks=range(0, 101, 10))

                        plt.plot(timestamps, self.lists[l], label=names[f])
                    elif l == "pps_recv" or l == "pps_sent":
                        if l == "pps_recv":
                            plt.ylabel("packets per second (received)")
                        else:
                            plt.ylabel("packets per second (sent)")

                        plt.xlim([0, 100])
                        plt.ylim([0, max(self.lists[l]) + 0.05 * max(self.lists[l])])

                        plt.plot(timestamps, self.lists[l], label=names[f])
                    else:
                        plt.plot(timestamps, self.lists[l], label=names[f])

                # reset data lists
                self.__reset_lists()

            if data_exists == False:
                print("No data in at least one of the files. Not printing the graph.")
            else:
                # create the graph with the picked data
                plt.legend()
                plt.savefig(os.path.join(full_path, l))
                plt.clf()
                print(f"File saved as {short_path}/{l}.png.")

    def __make_graph(self, file_name):
        self.__reset_lists()
        self.__fill_lists()
        timestamps = self.__get_timestamps()

        # TODO: Add way to plot multiple graphs into one graphic
        no_data = True
        for l in self.lists:
            if self.lists[l] != [] and l != "time":
                short_path = f"data_graphs/{file_name[:-5]}"
                file_path = os.path.join(os.getcwd(), short_path)
                Path(file_path).mkdir(parents=True, exist_ok=True)

                plt.grid(True, "both", "y")
                plt.xlabel("time [s]")
                plt.minorticks_on()

                if l == "bytes_recv" or l == "bytes_sent":
                    # get the unit of the maximum value and use it for all values
                    values = self.lists[l]
                    unit = self.__get_unit(max(values))

                    while max(values) > 1024:
                        for v in range(len(values)):
                            values[v] = values[v] / 1024

                    if l == "bytes_recv":
                        plt.ylabel(f"total bytes (received) [{unit}]")
                    else:
                        plt.ylabel(f"total bytes (sent) [{unit}]")

                    plt.xlim([0, max(timestamps)])
                    plt.ylim([0, max(values) + 0.05 * max(values)])

                    plt.plot(timestamps, values)
                elif l == "cpu_percent" or l == "ram_percent":
                    if l == "cpu_percent":
                        plt.ylabel("CPU usage [%]")
                    else:
                        plt.ylabel("RAM usage [%]")

                    if min(self.lists[l]) <= 15:
                        min_limit = 0
                    else:
                        min_limit = 0.95 * min(
                            self.lists[l]
                        )  # set min_limit to 5 percent less than the actual minimum

                    if max(self.lists[l]) >= 85:
                        max_limit = 100
                    else:
                        max_limit = 1.05 * max(
                            self.lists[l]
                        )  # set max_limit to 5 percent more than the actual maximum

                    plt.xlim([0, max(timestamps)])
                    plt.ylim([min_limit, max_limit])

                    plt.plot(timestamps, self.lists[l])
                elif l == "pps_recv" or l == "pps_sent":
                    if l == "pps_recv":
                        plt.ylabel("packets per second (received)")
                    else:
                        plt.ylabel("packets per second (sent)")

                    plt.xlim([0, max(timestamps)])
                    plt.ylim([0, max(self.lists[l]) + 0.05 * max(self.lists[l])])

                    plt.plot(timestamps, self.lists[l])
                else:
                    plt.plot(timestamps, self.lists[l])

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

    def __fill_lists(self):
        for i in range(len(self.data["data"])):
            self.lists["time"].append(self.__get_time_stamp(i))
            if self.cpu_percent == True:
                self.lists["cpu_percent"].append(self.__get_cpu_percent(i))
            if self.ram_percent == True:
                self.lists["ram_percent"].append(self.__get_ram_percent(i))
            if self.bytes_recv == True:
                self.lists["bytes_recv"].append(self.__get_bytes_recv(i))
            if self.bytes_sent == True:
                self.lists["bytes_sent"].append(self.__get_bytes_sent(i))
            if self.pps_recv == True:
                self.lists["pps_recv"].append(self.__get_pps_recv(i))
            if self.pps_sent == True:
                self.lists["pps_sent"].append(self.__get_pps_sent(i))

    def __get_timestamps(self):
        # get the times as difference from the initial time
        timestamps = [0.0]
        initial_time = datetime.fromisoformat(self.lists["time"][0])
        for i in range(1, len(self.lists["time"])):
            cur_time = datetime.fromisoformat(self.lists["time"][i])
            timestamps.append((cur_time - initial_time).total_seconds())

        return timestamps

    def __get_relative_timestamps(self):
        # get the times as difference from the initial time
        timestamps = [0.0]

        min_time = min(self.lists["time"])
        max_time = max(self.lists["time"])

        initial_time = datetime.fromisoformat(min_time)
        end_time = datetime.fromisoformat(max_time)
        for i in range(1, len(self.lists["time"])):
            cur_time = datetime.fromisoformat(self.lists["time"][i])
            timestamps.append(
                (
                    (cur_time - initial_time).total_seconds()
                    / (end_time - initial_time).total_seconds()
                )
                * 100
            )

        return timestamps

    def __get_unit(self, bytes):
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < 1024:
                if unit == "":
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


@click.command()
@click.option("--compare", default=0, help="number of files to compare")
@click.argument("path")
def cli(compare, path):
    questions = [
        inquirer.Checkbox(
            "values",
            message="What graphs should be created?",
            choices=[
                "all",
                "cpu_percent",
                "ram_percent",
                "bytes_recv",
                "bytes_sent",
                "pps_recv",
                "pps_sent",
            ],
        ),
    ]
    
    answers = inquirer.prompt(questions)
    # check if no boxes are checked
    if answers == None:
        print_err("Something went wrong!")
        return

    if "all" in answers["values"]:
        all = True
    else:
        all = False

    if compare == 0 or compare == 1:
        # if path is directory
        if os.path.isdir(path):
            output = DataOutput(
                cpu_percent="cpu_percent" in answers["values"] or all,
                ram_percent="ram_percent" in answers["values"] or all,
                bytes_recv="bytes_recv" in answers["values"] or all,
                bytes_sent="bytes_sent" in answers["values"] or all,
                pps_recv="pps_recv" in answers["values"] or all,
                pps_sent="pps_sent" in answers["values"] or all,
            )
            print("Creating graphs for all json files in the directory...")
            output.make_graphs_for_directory(path)
        # if path is json file
        elif os.path.isfile(path) and path[-5:] == ".json":
            output = DataOutput(
                cpu_percent="cpu_percent" in answers["values"] or all,
                ram_percent="ram_percent" in answers["values"] or all,
                bytes_recv="bytes_recv" in answers["values"] or all,
                bytes_sent="bytes_sent" in answers["values"] or all,
                pps_recv="pps_recv" in answers["values"] or all,
                pps_sent="pps_sent" in answers["values"] or all,
            )
            print("Creating graphs for the file...")
            output.make_graphs_for_file(path)
        # if path is other file
        elif os.path.exists(path):
            print_err("The given file is not a json file.")
        # path does not exist
        else:
            print_err("The given path does not exist.")
    elif compare >= 2:
        output = DataOutput(
            cpu_percent="cpu_percent" in answers["values"] or all,
            ram_percent="ram_percent" in answers["values"] or all,
            bytes_recv="bytes_recv" in answers["values"] or all,
            bytes_sent="bytes_sent" in answers["values"] or all,
            pps_recv="pps_recv" in answers["values"] or all,
            pps_sent="pps_sent" in answers["values"] or all,
        )
        output.compare_graphs(path, compare)
    else:
        return


if __name__ == "__main__":
    cli()
