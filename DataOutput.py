import json
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
from datetime import datetime
from helpers.messages import print_err, print_warn, print_log
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import click
import inquirer


class DataOutput:
    # lists for the values
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

    # public methods
    def make_graphs_for_directory(self, dir_path, full, median):
        # goes through files in a directory and calls make_graphs_for_file
        try:
            files_exist = False

            # check if path exists and is a directory
            if not os.path.isdir(dir_path):
                raise NotADirectoryError

            for file in os.listdir(dir_path):
                # check if file is a json
                if file[-5:] == ".json":
                    files_exist = True
                    file_path = dir_path + "/" + file
                    self.make_graphs_for_file(file_path, full, median)
                    plt.close()

            if not files_exist:
                raise FileNotFoundError
        except NotADirectoryError:
            print_err("The given path is not a directory.")
            return
        except FileNotFoundError:
            print_err("The given directory does not contain json files.")
            return
        except KeyError:
            print_err("At least one of the json files does not contain correct data.")
            return
        except Exception as err:
            print_err(f"Unexpected {err=}, {type(err)=}")
            return

    def make_graphs_for_file(self, file_path, full, median):
        self.file_name = os.path.basename(file_path)
        try:
            self.__check_file_name_and_set_attributes(self.file_name)
            self.file = open(file_path)
            self.data = json.load(self.file)
        except IsADirectoryError:
            print_err(f"Skipping {file_path}: The given path is not a json file.")
            return
        except FileNotFoundError:
            if self.file_name[-5:] == ".json":
                print_err(f"Skipping {file_path}: The given path is not a file.")
            else:
                print_err(f"Skipping {file_path}: The given path is not a json file.")
            return
        except Exception as err:
            print_err(f"Unexpected {err=}, {type(err)=}")
            return

        self.__make_graph(self.file_name, full, median)

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
                    bytes_recv = self.__get_bytes_recv(i)
                    bytes_sent = self.__get_bytes_sent(i)
                    if bytes_recv != None and bytes_sent != None:
                        cur_b_recv = bytes_recv
                        cur_b_sent = bytes_sent
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
                        self.lists["time"].append(self.__get_timestamp(i))

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

                if (
                    self.lists[l] != [] and l != "time"
                ):  # make sure the file contains data that is not timestamps
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
                        plt.yticks(ticks=np.arange(0, 101, 10))

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

    def __make_graph(self, file_name, full, median):
        # check if 'data' is correct
        if not self.__check_data():
            return

        # check file name and set attributes short_file_name, role and vpn_option
        if self.__check_file_name_and_set_attributes(file_name) == False:
            return

        # get path names and create directory
        graph_dir_path = (
            f"data_graphs/{self.short_file_name}"  # directory path for the graph
        )
        long_graph_dir_path = os.path.join(os.getcwd(), graph_dir_path)

        # get the data from the file
        timestamps = self.__fill_data_and_return_timestamps()

        always_full = False  # True if value type is not relative but absolute
        no_data = True  # True if self.lists is empty

        for value in self.lists:
            if self.lists[value] != [] and value != "time":
                title = ""  # build the title depending on values
                graph_file_path = (
                    long_graph_dir_path  # build the file path depending on values
                )

                # set plot parameters: grid
                plt.grid(True, "both", "y")
                if not median:
                    plt.minorticks_on()

                if value == "bytes_recv" or value == "bytes_sent":  # absolute values
                    always_full = True

                    # get the unit of the maximum value and use it for all values
                    values = self.lists[value]
                    unit = self.__get_unit(max(values))

                    while max(values) > 1024:
                        for v in range(len(values)):
                            values[v] = values[v] / 1024

                    # set plot parameters: ylabel
                    if value == "bytes_recv":
                        plt.ylabel(f"total bytes (received) [{unit}]")
                        title += "Total received bytes "
                    else:
                        plt.ylabel(f"total bytes (sent) [{unit}]")
                        title += "Total sent bytes "

                    # set plot parameters: ylimits
                    plt.ylim([0, 1.05 * max(values)])

                    if median:
                        data = self.__partition_data(self.lists[value])

                        if data == None:
                            print_err("  Data is empty. Not printing the graph.")
                            return

                        # set plot parameters: xlabel
                        plt.xlabel(
                            "#time interval (of length {:.3f} s)".format(data[1])
                        )

                        # plot
                        plt.boxplot(
                            data[0],
                            showfliers=True,
                            flierprops=dict(marker="x", markeredgecolor="lightgrey"),
                            medianprops=dict(color="blue", linewidth=1.5),
                        )
                    else:
                        # set plot parameters: xlabel, xlimits
                        plt.xlabel("time [s]")
                        plt.xlim([0, self.length])

                        # plot
                        plt.plot(timestamps, self.lists[value])
                elif (
                    value == "cpu_percent" or value == "ram_percent"
                ):  # relative values
                    # set plot parameters: ylabel
                    if value == "cpu_percent":
                        plt.ylabel("CPU usage [%]")
                        title += f"CPU usage "
                    else:
                        plt.ylabel("RAM usage [%]")
                        title += f"RAM usage "

                    # set initial min and max ylimit
                    min_limit = 0
                    max_limit = 100

                    # if detailed, set new ylimits
                    if not full:
                        if min(self.lists[value]) > 15:
                            min_limit = 0.95 * min(
                                self.lists[value]
                            )  # set min_limit to 5 percent less than the actual minimum

                        if max(self.lists[value]) < 85:
                            max_limit = 1.05 * max(
                                self.lists[value]
                            )  # set max_limit to 5 percent more than the actual maximum

                    # set plot parameters: ylimits
                    plt.ylim([min_limit, max_limit])

                    if median:
                        data = self.__partition_data(self.lists[value])

                        if data == None:
                            print_err("  Data is empty. Not printing the graph.")
                            return

                        # set plot parameters: xlabel
                        plt.xlabel(
                            "#time interval (of length {:.3f} s)".format(data[1])
                        )

                        # plot
                        plt.boxplot(
                            data[0],
                            showfliers=True,
                            flierprops=dict(marker="x", markeredgecolor="lightgrey"),
                            medianprops=dict(color="blue", linewidth=1.5),
                        )
                    else:
                        # set plot parameters: xlabel, xlimits
                        plt.xlabel("time [s]")
                        plt.xlim([0, self.length])

                        # plot
                        plt.plot(timestamps, self.lists[value])
                elif value == "pps_recv" or value == "pps_sent":  # absolute values
                    always_full = True

                    # set plot parameters: ylabel
                    if value == "pps_recv":
                        plt.ylabel("packets per second (received)")
                        title += f"Received PPS "
                    else:
                        plt.ylabel("packets per second (sent)")
                        title += f"Sent PPS "

                    # set plot parameters: ylimits
                    plt.ylim(
                        [0, max(self.lists[value]) + 0.05 * max(self.lists[value])]
                    )

                    if median:
                        data = self.__partition_data(self.lists[value])

                        if data == None:
                            print_err("  Data is empty. Not printing the graph.")
                            return

                        # set plot parameters: xlabel
                        plt.xlabel(
                            "#time interval (of length {:.3f} s)".format(data[1])
                        )

                        # plot
                        plt.boxplot(
                            data[0],
                            showfliers=True,
                            flierprops=dict(marker="x", markeredgecolor="lightgrey"),
                            medianprops=dict(color="blue", linewidth=1.5),
                        )
                    else:
                        # set plot parameters: xlabel, xlimits
                        plt.xlabel("time [s]")
                        plt.xlim([0, self.length])

                        # plot
                        plt.plot(timestamps, self.lists[value])
                else:
                    print_err(f"  Unknown performance parameter '{value}'.")
                    return

                # adjust title
                if self.vpn_option == "novpn":
                    title += "without VPN "
                elif self.vpn_option == "rosenpass":
                    title += "using Rosenpass "
                else:
                    title += f"(VPN: {self.vpn_option}) "
                title += f"({self.role.capitalize()}, "
                title += "{:.1f} s)".format(self.length)

                # group data in subdirectories 'hardware' and 'network'
                if value == "cpu_percent" or value == "ram_percent":
                    graph_file_path = os.path.join(graph_dir_path, "hardware", value)
                elif (
                    value == "bytes_recv"
                    or value == "bytes_sent"
                    or value == "pps_recv"
                    or value == "pps_sent"
                ):
                    graph_file_path = os.path.join(graph_dir_path, "network", value)
                else:
                    graph_file_path = os.path.join(graph_dir_path, value)

                specific_value = value

                if median:
                    specific_value += "_median"
                    title += " (min/max/median)"

                if full and not always_full:
                    specific_value += "_full"

                # set plot parameters: title
                plt.title(title, fontweight="bold", fontsize=9)

                # create subdirectory and save plot in file
                Path(graph_file_path).mkdir(parents=True, exist_ok=True)
                plt.savefig(os.path.join(graph_file_path, specific_value))
                print_log(
                    f"  File saved as {graph_dir_path}/{value}/{specific_value}.png."
                )

                # clean up
                plt.clf()
                no_data = False
        if no_data == True:
            print_warn("  No data. Not printing any graphs.")

        # reset data lists
        self.__reset_lists()

    def __check_data(self):
        try:
            # check if there is only one field 'data'
            if len(self.data) != 1 or not isinstance(self.data["data"], list):
                raise KeyError

            if len(self.data["data"]) < 1:
                raise KeyError

            for dictionary in self.data["data"]:
                if not isinstance(dictionary, dict) or len(dictionary) != 4:
                    raise KeyError

                # check hardware values
                if (
                    not isinstance(dictionary["hardware"], list)
                    or len(dictionary["hardware"]) != 1
                    or not isinstance(dictionary["hardware"][0], dict)
                    or len(dictionary["hardware"][0]) != 2
                    or not isinstance(dictionary["hardware"][0]["cpu_percent"], float)
                    or not isinstance(dictionary["hardware"][0]["ram_percent"], float)
                ):
                    raise KeyError

                # check network values
                if (
                    not isinstance(dictionary["network"], list)
                    or len(dictionary["network"]) != 1
                    or not isinstance(dictionary["network"][0], dict)
                    or len(dictionary["network"][0]) != 4
                    or not isinstance(dictionary["network"][0]["bytes_recv"], int)
                    or not isinstance(dictionary["network"][0]["bytes_sent"], int)
                    or not isinstance(dictionary["network"][0]["pps_recv"], int)
                    or not isinstance(dictionary["network"][0]["pps_sent"], int)
                ):
                    raise KeyError

                # check timestamp
                datetime.fromisoformat(dictionary["time"])

                # check name
                if not isinstance(dictionary["name"], str):
                    raise KeyError

        except KeyError:
            print_warn(f"  Skipping file {self.file_name}: Incorrect or no data!")
            return False
        except ValueError:
            print_warn(f"  Skipping file {self.file_name}: Incorrect timestamp format!")
            return False
        except Exception as err:
            print_err(f"  Unexpected {err=}, {type(err)=}")
            return False

        return True

    # check that the file_name has the format 'client-novpn:2024-01-04T12:29:19.843495.json'
    def __check_file_name_and_set_attributes(self, file_name):
        try:
            if file_name[-5:] != ".json":
                raise KeyError
            self.short_file_name = file_name[:-5]
            tmp_split_name = self.short_file_name.split(":")

            if len(tmp_split_name) != 4:
                raise KeyError

            role_and_vpn_option = tmp_split_name[0]

            # check timestamp
            datetime.fromisoformat(
                f"{tmp_split_name[1]}:{tmp_split_name[2]}:{tmp_split_name[3]}"
            )

            tmp_split_name = role_and_vpn_option.split("-")
            if (
                len(tmp_split_name) != 2
                or not isinstance(tmp_split_name[0], str)
                or not isinstance(tmp_split_name[1], str)
            ):
                raise KeyError

            self.role, self.vpn_option = tmp_split_name

        except KeyError:
            print_warn(
                f"  Skipping {file_name}: The format of the file name is incorrect."
            )
            return False
        except ValueError:
            print_warn(
                f"  Skipping {file_name}: The format of the file name is incorrect: wrong timestamp format."
            )
            return False
        except TypeError:
            print_warn(f"  Skipping {file_name}: Not a file name.")
            return False
        except Exception as err:
            print_err(f"  Unexpected {err=}, {type(err)=}")
            return False

        return True

    def __fill_data_and_return_timestamps(self):
        self.__reset_lists()
        self.__fill_lists()
        timestamps = self.__get_timestamps()
        self.length = max(timestamps)

        return timestamps

    def __reset_lists(self):
        for l in self.lists:
            self.lists[l] = []

    def __partition_data(self, initial_data, number_blocks=8):
        data = []
        sub_data = []

        sub_time = self.length / number_blocks  # length of each interval
        cur_time = sub_time  # use data up to this time, then go to next interval
        timestamp = self.__get_timestamp(0)

        # check timestamp
        try:
            if not isinstance(timestamp, str):
                raise KeyError

            initial_time = datetime.fromisoformat(timestamp)
        except:
            print_err("  Incorrect timestamp.")
            return

        i = 0
        while i < len(initial_data):
            timestamp = self.__get_timestamp(i)

            try:
                if not isinstance(timestamp, str):
                    raise KeyError

                time = datetime.fromisoformat(timestamp)

                if (
                    time - initial_time
                ).total_seconds() > cur_time:  # if all values in interval have been added
                    data.append(sub_data)
                    sub_data = []
                    cur_time += sub_time
                    continue
            except:
                print_err("  Incorrect timestamp.")
                return

            sub_data.append(initial_data[i])
            i += 1

        timestamp = self.__get_timestamp(len(initial_data) - 1)

        try:
            if not isinstance(timestamp, str):
                raise KeyError

            time = datetime.fromisoformat(timestamp)

            if (time - initial_time).total_seconds() <= cur_time:
                data.append(sub_data)
        except:
            print_err("  Incorrect timestamp.")
            return

        return (data, sub_time)

    def __fill_lists(self):
        if not self.__check_data():
            return

        for i in range(len(self.data["data"])):
            self.lists["time"].append(self.__get_timestamp(i))
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
        # get the times as absolute difference from the initial time
        timestamps = [0.0]
        initial_time = datetime.fromisoformat(self.lists["time"][0])
        for i in range(1, len(self.lists["time"])):
            cur_time = datetime.fromisoformat(self.lists["time"][i])
            timestamps.append((cur_time - initial_time).total_seconds())

        return timestamps

    def __get_relative_timestamps(self):
        # get the times as relative difference from the initial time
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
        print_err("  Number of bytes is too large!")

    def __get_timestamp(self, entry):
        try:
            return self.data["data"][entry]["time"]
        except:
            print_err("  Could not get timestamp.")

    def __get_cpu_percent(self, entry):
        try:
            return self.data["data"][entry]["hardware"][0]["cpu_percent"]
        except:
            print_err("  Could not get cpu percent value.")

    def __get_ram_percent(self, entry):
        try:
            return self.data["data"][entry]["hardware"][0]["ram_percent"]
        except:
            print_err("  Could not get ram percent value.")

    def __get_bytes_recv(self, entry):
        try:
            return self.data["data"][entry]["network"][0]["bytes_recv"]
        except:
            print_err("  Could not get bytes recv value.")

    def __get_bytes_sent(self, entry):
        try:
            return self.data["data"][entry]["network"][0]["bytes_sent"]
        except:
            print_err("  Could not get bytes sent value.")

    def __get_pps_recv(self, entry):
        try:
            return self.data["data"][entry]["network"][0]["pps_recv"]
        except:
            print_err("  Could not get pps recv value.")

    def __get_pps_sent(self, entry):
        try:
            return self.data["data"][entry]["network"][0]["pps_sent"]
        except:
            print_err("  Could not get pps sent value.")


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
        inquirer.List(
            "full",
            message="Create full or detailed graphs?",
            choices=[
                "both",
                "only full graphs (0 to 100 percent)",
                "only detailed graphs",
            ],
        ),
        inquirer.List(
            "median",
            message="Create min/max/median graphs?",
            choices=[
                "both",
                "only min/max/median graphs",
                "only normal graphs",
            ],
        ),
    ]

    answers = inquirer.prompt(questions)
    # check if no boxes are checked
    if answers == None:
        print_err("Something went wrong!")
        return

    for a in answers:
        if a == None:
            print_err("Something went wrong!")
            return

    if "all" in answers["values"]:
        all = True
    else:
        all = False

    if answers["full"] == "only full graphs (0 to 100 percent)":
        full_graphs = True
        detailed_graphs = False
    elif answers["full"] == "only detailed graphs":
        full_graphs = False
        detailed_graphs = True
    else:
        full_graphs = True
        detailed_graphs = True

    if answers["median"] == "only min/max/median graphs":
        median_graphs = True
        normal_graphs = False
    elif answers["median"] == "only normal graphs":
        median_graphs = False
        normal_graphs = True
    else:
        median_graphs = True
        normal_graphs = True

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
            if full_graphs and median_graphs:
                output.make_graphs_for_directory(path, full=True, median=True)
            if full_graphs and normal_graphs:
                output.make_graphs_for_directory(path, full=True, median=False)
            if detailed_graphs and median_graphs:
                output.make_graphs_for_directory(path, full=False, median=True)
            if detailed_graphs and normal_graphs:
                output.make_graphs_for_directory(path, full=False, median=False)
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
            if full_graphs and median_graphs:
                output.make_graphs_for_file(path, full=True, median=True)
            if full_graphs and normal_graphs:
                output.make_graphs_for_file(path, full=True, median=False)
            if detailed_graphs and median_graphs:
                output.make_graphs_for_file(path, full=False, median=True)
            if detailed_graphs and normal_graphs:
                output.make_graphs_for_file(path, full=False, median=False)
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
