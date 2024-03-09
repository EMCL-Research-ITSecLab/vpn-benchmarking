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
        return ""

    def get_name_string(self) -> str:
        messages.print_err("ValueType.get_name_string(self): NOT IMPLEMENTED")
        return ""

    def get_x_label(self) -> str:
        if not self.median:
            return "time [s]"

        messages.print_err("ValueType.get_x_label(self): NOT IMPLEMENTED")
        return ""

    def get_y_label(self) -> str:
        messages.print_err("ValueType.get_y_label(self): NOT IMPLEMENTED")
        return ""

    def get_x_limit(self) -> list:
        if not self.median:
            return [0, self.length - 1]

        messages.print_err("ValueType.get_x_limit(self): NOT IMPLEMENTED")
        return [0, 0]

    def get_y_limit(self) -> list:
        messages.print_err("ValueType.get_y_limit(self): NOT IMPLEMENTED")
        return [0, 0]

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
    def get_y_limit(self) -> list:
        return [0, 1.05 * max(self.values)]


class CPUPercent(RelativeValueType):
    def get_name_string(self) -> str:
        return "cpu_percent"

    def get_category_string(self) -> str:
        return "hardware"

    def get_y_label(self) -> str:
        return "CPU usage [%]"


class RAMPercent(RelativeValueType):
    def get_name_string(self) -> str:
        return "ram_percent"

    def get_category_string(self) -> str:
        return "hardware"

    def get_y_label(self) -> str:
        return "RAM usage [%]"


class RecvBytes(AbsoluteValueType):
    def get_name_string(self) -> str:
        return "bytes_recv"

    def get_category_string(self) -> str:
        return "network"

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

    def get_y_label(self) -> str:
        return "packets per second (received)"


class SentPPS(AbsoluteValueType):
    def get_name_string(self) -> str:
        return "pps_sent"

    def get_category_string(self) -> str:
        return "network"

    def get_y_label(self) -> str:
        return "packets per second (sent)"


class SingleGraphGenerator:
    """
    Generates a graph from given data and adds it to an existing plot.
    """

    def __init__(self, value_type, timestamps: list, values: list, full: bool, median: bool) -> None:
        self.value_instance = value_type(values, full, median)
        self.timestamps = timestamps
        self.values = values
        self.full = full
        self.median = median

    def plot_graph(self):
        values = self.value_instance.get_adjusted_values()
        self.__adjust_basic_plot_settings()
        self.__set_x_label(self.value_instance.get_x_label())
        self.__set_y_label(self.value_instance.get_y_label())
        self.__set_x_limit(self.value_instance.get_x_limit())
        self.__set_y_limit(self.value_instance.get_y_limit())
        # maybe set ticks
        self.__plot(values)

    def __plot(self, values):
        if not self.median:
            plt.plot(self.timestamps, values)

        # TODO

    def __adjust_basic_plot_settings(self):
        plt.grid(True, "both", "y")  # turn on y-axis grid
        plt.minorticks_on()  # turn on ticks

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
        plt.ylim(limits)


class SingleFileGraphHandler:  # TODO: should maybe inherit from DataOutput
    value_lists = {}

    def __init__(self, file_path, value_types: list) -> None:
        """
        :param value_types: list of ValueTypes for which a graph should be generated
        """
        self.value_types = value_types

        if not os.path.isfile(file_path):
            messages.print_warn(f"{file_path} is not a file.")
            return

        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        if not self.file_name[-5:] == ".json":
            messages.print_warn(f"{file_path} is not a JSON file.")
            return
        self.short_file_name = self.file_name[:-5]

        if not self.__load_data_from_file():
            raise Exception("Unable to load data from file!")
        if not self.__fill_lists_from_data():
            raise Exception(f"Incorrect data format in {self.file_path}")

    def generate_graphs(self, full: bool, median: bool):
        graph_dir_path = os.path.join("data_graphs", self.short_file_name)  # directory path for the graph

        for value_type in self.value_types:
            name_string = value_type.get_name_string(value_type)

            generator = SingleGraphGenerator(
                value_type=value_type,
                timestamps=self.value_lists["time"],
                values=self.value_lists[name_string],
                full=full,
                median=median,
            )

            generator.plot_graph()
            # TODO: Put into method
            graph_file_path = os.path.join(graph_dir_path, name_string)
            Path(graph_file_path).mkdir(parents=True, exist_ok=True)
            plt.savefig(graph_file_path)
            plt.clf()

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


sgh = SingleFileGraphHandler("data.json", [CPUPercent, RAMPercent])
sgh.generate_graphs(False, False)
