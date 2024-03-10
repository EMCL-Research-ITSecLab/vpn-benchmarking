import json
import os.path
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

import messages


def get_smallest_bytes_unit(n):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if n < 1024:
            if unit == "":
                return "B"
            else:
                return f"{unit}iB"
        n = n / 1024
    messages.print_err("Number of bytes is too large!")


class ValueType:
    def __init__(self, values: list, full: bool, median: bool) -> None:
        self.values = values
        self.length = len(values)
        self.full = full
        self.median = median

    def get_category_string(self) -> str:
        messages.print_err("ValueType.get_category_string(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_name_string(self) -> str:
        messages.print_err("ValueType.get_name_string(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_description(self) -> str:
        messages.print_err("ValueType.get_description(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_x_label(self, interval_length=None) -> str:
        if self.median:
            return "#time interval (of length {:.3f} s)".format(interval_length)

        return "time [s]"

    def get_y_label(self) -> str:
        messages.print_err("ValueType.get_y_label(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_x_limit(self, max_value) -> list:
        if not self.median:
            return [0, max_value]

        messages.print_err("x-limit for median graphs is automatically set.")
        raise ValueError

    def get_y_limit(self) -> list:
        messages.print_err("ValueType.get_y_limit(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_adjusted_values(self) -> list:
        """
        If needed, can be used to adjust the values (e.g. to a different unit). Simply returns unchanged values in
        base implementation.
        :return: list of adjusted values
        """
        return self.values


class RelativeValueType(ValueType):
    def get_y_limit(self) -> list:
        if self.full:
            return [0, 100]

        # set initial min and max y-limit
        min_limit = 0
        max_limit = 100

        if min(self.values) > 15:
            min_limit = 0.95 * min(self.values)  # set min_limit to 5 percent less than the actual minimum

        if max(self.values) < 85:
            max_limit = 1.05 * max(self.values)  # set max_limit to 5 percent more than the actual maximum

        return [min_limit, max_limit]


class AbsoluteValueType(ValueType):
    def get_y_limit(self) -> list | None:
        if not max(self.values):
            return None
        return [0, 1.05 * max(self.values)]


class CPUPercent(RelativeValueType):
    def get_name_string(self) -> str:
        return "cpu_percent"

    def get_category_string(self) -> str:
        return "hardware"

    def get_description(self) -> str:
        return "CPU usage"

    def get_y_label(self) -> str:
        return "CPU usage [%]"


class RAMPercent(RelativeValueType):
    def get_name_string(self) -> str:
        return "ram_percent"

    def get_category_string(self) -> str:
        return "hardware"

    def get_description(self) -> str:
        return "RAM usage"

    def get_y_label(self) -> str:
        return "RAM usage [%]"


class RecvBytes(AbsoluteValueType):
    def get_name_string(self) -> str:
        return "bytes_recv"

    def get_category_string(self) -> str:
        return "network"

    def get_description(self) -> str:
        return "Total received bytes"

    def get_y_label(self) -> str:
        unit = get_smallest_bytes_unit(max(self.values))
        return f"total bytes (received) [{unit}]"

    def get_adjusted_values(self) -> list:
        values = self.values

        while max(values) > 1024:
            for v in range(len(values)):
                values[v] = values[v] / 1024

        return values


class SentBytes(AbsoluteValueType):
    def get_name_string(self) -> str:
        return "bytes_sent"

    def get_category_string(self) -> str:
        return "network"

    def get_description(self) -> str:
        return "Total sent bytes"

    def get_y_label(self) -> str:
        unit = get_smallest_bytes_unit(max(self.values))
        return f"total bytes (sent) [{unit}]"

    def get_adjusted_values(self) -> list:
        values = self.values

        while max(values) > 1024:
            for v in range(len(values)):
                values[v] = values[v] / 1024

        return values


class RecvPPS(AbsoluteValueType):
    def get_name_string(self) -> str:
        return "pps_recv"

    def get_category_string(self) -> str:
        return "network"

    def get_description(self) -> str:
        return "Received PPS"

    def get_y_label(self) -> str:
        return "packets per second (received)"


class SentPPS(AbsoluteValueType):
    def get_name_string(self) -> str:
        return "pps_sent"

    def get_category_string(self) -> str:
        return "network"

    def get_description(self) -> str:
        return "Sent PPS"

    def get_y_label(self) -> str:
        return "packets per second (sent)"


class SingleGraphGenerator:
    """
    Generates a graph from given data and adds it to an existing plot.
    """

    def __init__(self, value_type, timestamps: list, values: list, full: bool, median: bool, title: str = "") -> None:
        if not len(timestamps) == len(values):
            raise ValueError

        self.value_instance = value_type(values, full, median)
        self.timestamps = timestamps
        self.values = values
        self.full = full
        self.median = median
        self.title = title

    def plot_graph(self):
        values = self.value_instance.get_adjusted_values()
        max_timestamp = max(self.__get_timestamps_as_absolute_difference())

        self.__adjust_basic_plot_settings()

        # only median x-label needs interval_length argument
        if self.median:
            _, interval_length = self.__partition_data(values)
            self.__set_x_label(self.value_instance.get_x_label(interval_length))
        else:
            self.__set_x_label(self.value_instance.get_x_label())

        self.__set_y_label(self.value_instance.get_y_label())

        if not self.median:
            self.__set_x_limit(self.value_instance.get_x_limit(max_timestamp))

        self.__set_y_limit(self.value_instance.get_y_limit())

        if self.title:
            self.__set_title()

        self.__plot(values)

    def __plot(self, values):
        if self.median:
            partitioned_data, _ = self.__partition_data(values)
            plt.boxplot(
                partitioned_data,
                showfliers=True,
                flierprops=dict(marker="x", markeredgecolor="lightgrey"),
                medianprops=dict(color="blue", linewidth=1.5),
            )
            return

        timestamps = self.__get_timestamps_as_absolute_difference()
        plt.plot(timestamps, values)

    def __get_timestamps_as_absolute_difference(self) -> list[float]:
        """
        Return the timestamps as absolute differences from the initial time.
        :return: list of absolute timestamps starting from 0.0
        """
        timestamps = [0.0]
        initial_time = datetime.fromisoformat(self.timestamps[0])

        for i in range(1, len(self.timestamps)):
            cur_time = datetime.fromisoformat(self.timestamps[i])
            timestamps.append((cur_time - initial_time).total_seconds())

        return timestamps

    def __adjust_basic_plot_settings(self):
        plt.grid(True, "both", "y")  # turn on y-axis grid
        plt.minorticks_on()  # turn on ticks

    def __partition_data(self, initial_data, number_blocks=8):
        def calculate_block_number():
            result = int((time_value * number_blocks) // full_time)

            if result == number_blocks:  # the last value should be part of the last block
                return number_blocks - 1

            return result

        resulting_data = []  # has number_blocks many empty data blocks
        for _ in range(number_blocks):
            resulting_data.append([])  # appends number_block empty lists

        timestamps = self.__get_timestamps_as_absolute_difference()
        full_time = max(timestamps)
        interval_length = full_time / number_blocks

        for i in range(len(initial_data)):
            time_value = timestamps[i]
            resulting_data[calculate_block_number()].append(initial_data[i])

        return resulting_data, interval_length

    def __set_title(self):
        plt.title(self.title, fontweight="bold", fontsize=9)

    def __set_x_label(self, text):
        """
        Sets the x-label of the plot to text.
        :param text: x-label text
        """
        plt.xlabel(text)

    def __set_y_label(self, text):
        """
        Sets the y-label of the plot to text.
        :param text: y-label text
        """
        plt.ylabel(text)

    def __set_x_limit(self, limits: list):
        """
        Sets the x-limit of the plot to the two values given in limits.
        :param limits: list of the two x-limits (min- and max-limit)
        """
        plt.xlim(limits)

    def __set_y_limit(self, limits: list):
        """
        Sets the y-limit of the plot to the two values given in limits.
        :param limits: list of the two y-limits (min- and max-limit)
        """
        if limits:
            plt.ylim(limits)


class SingleFileGraphHandler:  # TODO: should maybe inherit from DataOutput
    def __init__(self, file_path, value_types: list) -> None:
        """
        TODO
        :param value_types: list of ValueTypes for which a graph should be generated
        """
        self.value_lists = {}
        self.value_types = value_types

        if not os.path.isfile(file_path):
            messages.print_warn(f"{file_path} is not a file.")
            return

        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        if self.file_name[-5:] != ".json":
            messages.print_warn(f"{file_path} is not a JSON file.")
            return
        self.short_file_name = self.file_name[:-5]

        if not self.__load_data_from_file():
            raise Exception("Unable to load data from file!")
        if not self.__fill_lists_from_data():
            raise Exception(f"Incorrect data format in {self.file_path}")

    def generate_graphs(self, full: bool, median: bool):
        def calculate_full_time() -> float:
            initial_time = datetime.fromisoformat(self.value_lists["time"][0])
            last_time = datetime.fromisoformat(self.value_lists["time"][len(self.value_lists["time"]) - 1])
            return (last_time - initial_time).total_seconds()

        graph_dir_path = os.path.join("data_graphs", self.short_file_name)

        for value_type in self.value_types:
            name_string = value_type.get_name_string(value_type)
            category_string = value_type.get_category_string(value_type)

            title = self.__get_title(value_type, calculate_full_time(), median)

            generator = SingleGraphGenerator(
                value_type=value_type,
                timestamps=self.value_lists["time"],
                values=self.value_lists[name_string],
                full=full,
                median=median,
                title=title,
            )

            generator.plot_graph()
            file_path = os.path.join(graph_dir_path, category_string, name_string)
            file_name = self.__generate_filename(value_type, full, median)
            self.__save_figure(file_path, file_name)

    def __generate_filename(self, value_type, full: bool, median: bool) -> str:
        if issubclass(value_type, RelativeValueType):
            if full and median:
                return "full_min-max-median"
            if full:
                return "full"

        if median:
            return "min-max-median"

        return "normal"

        # bytes_recv/
        #     normal
        #     full
        #     min-max-median
        #     full_min-max-median

    def __save_figure(self, file_path, file_name):
        Path(file_path).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(file_path, file_name))
        plt.clf()
        self.__clean_up()

    def __get_title(self, value_type, full_time: float, median: bool) -> str:
        def check_filename_format() -> bool:
            tmp_split_name = self.short_file_name.split("_")

            if len(tmp_split_name) != 4:
                return False

            role_and_vpn_option = tmp_split_name[0]

            try:
                datetime.fromisoformat(
                    f"{tmp_split_name[1]}:{tmp_split_name[2]}:{tmp_split_name[3]}"
                )
            except Exception as err:
                print(f"{err=}")
                return False

            tmp_split_name = role_and_vpn_option.split("-")
            if (
                    len(tmp_split_name) != 2
                    or not isinstance(tmp_split_name[0], str)
                    or not isinstance(tmp_split_name[1], str)
            ):
                return False

            return True

        def get_info_from_filename() -> [str, str]:
            tmp_split_name = self.short_file_name.split("_")
            role_and_vpn_option = tmp_split_name[0]
            role, vpn_option = role_and_vpn_option.split("-")
            return role, vpn_option

        full_time = "{:.1f}".format(full_time)
        value_type_information = value_type.get_description(value_type)
        median_information = ""
        if median:
            median_information = " (min/max/median)"

        if not check_filename_format():
            return f"{value_type_information} ({full_time} s){median_information}"

        vpn_information = f"(VPN: {get_info_from_filename()[1]})"
        role_information = get_info_from_filename()[0].capitalize()

        return f"{value_type_information} {vpn_information} ({role_information}, {full_time} s){median_information}"

    def __load_data_from_file(self) -> bool:
        try:
            file = open(self.file_path)
        except Exception as err:
            print(f"{err=}")
            return False

        try:
            self.data = json.load(file)
        except Exception as err:
            print(f"{err=}")
            return False

        return True

    def __fill_lists_from_data(self) -> bool:
        if not self.__validate_data():
            return False

        self.value_lists["time"] = []
        for i in range(len(self.data["data"])):
            # add timestamp entry
            self.value_lists["time"].append(self.__get_single_timestamp(i))

            # add value entries
            for value_type in self.value_types:
                name_string = value_type.get_name_string(value_type)
                category_string = value_type.get_category_string(value_type)

                # avoid overwriting existing entries
                try:
                    entry = self.data["data"][i][category_string][0][name_string]
                    self.value_lists[name_string].append(entry)
                except KeyError:
                    self.value_lists[name_string] = []  # would overwrite values
                    entry = self.data["data"][i][category_string][0][name_string]
                    self.value_lists[name_string].append(entry)

        return True

    def __validate_data(self) -> bool:
        def check_data_fields():
            # check if there is only one field 'data'
            if len(self.data) != 1 or not isinstance(self.data["data"], list):
                raise KeyError

            if len(self.data["data"]) < 1:
                raise KeyError

        def check_dictionary_size():
            if not isinstance(dictionary, dict) or len(dictionary) != 4:
                raise KeyError

        def check_hardware_values():
            if (
                    not isinstance(dictionary["hardware"], list)
                    or len(dictionary["hardware"]) != 1
                    or not isinstance(dictionary["hardware"][0], dict)
                    or len(dictionary["hardware"][0]) != 2
                    or not isinstance(dictionary["hardware"][0]["cpu_percent"], float)
                    or not isinstance(dictionary["hardware"][0]["ram_percent"], float)
            ):
                raise KeyError

        def check_network_values():
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

        def check_timestamp():
            datetime.fromisoformat(dictionary["time"])

        def check_name():
            if not isinstance(dictionary["name"], str):
                raise KeyError

        try:
            check_data_fields()

            for dictionary in self.data["data"]:
                check_dictionary_size()
                check_hardware_values()
                check_network_values()
                check_timestamp()
                check_name()

            return True
        except KeyError:
            messages.print_warn(f"File {self.file_name} has incorrect or no data!")
            return False
        except ValueError:
            messages.print_warn(f"File {self.file_name} has incorrect timestamp format!")
            return False
        except Exception as err:
            print(f"{err=}")
            return False

    def __get_single_timestamp(self, n: int):
        return self.data["data"][n]["time"]

    def __clean_up(self):
        self.value_lists = {}

        if not self.__load_data_from_file():
            raise Exception("Unable to load data from file!")
        if not self.__fill_lists_from_data():
            raise Exception(f"Incorrect data format in {self.file_path}")


class MultiFileGraphHandler:
    def __init__(self, path, value_types: list) -> None:
        """
        TODO
        :param value_types: list of ValueTypes for which a graph should be generated
        """

        if not (os.path.isdir(path) or os.path.isfile(path)):
            messages.print_warn(f"{path} is not a valid path.")
            return

        self.path = path
        self.value_types = value_types

    def generate_graphs(self, full: bool, median: bool):
        if os.path.isdir(self.path):
            for file_name in os.listdir(self.path):
                single_file_handler = SingleFileGraphHandler(os.path.join(self.path, file_name), self.value_types)
                single_file_handler.generate_graphs(full, median)

                del single_file_handler


mgh = MultiFileGraphHandler("data",
                            [CPUPercent, RAMPercent, RecvBytes, RecvPPS, SentPPS, SentBytes])
mgh.generate_graphs(True, True)
