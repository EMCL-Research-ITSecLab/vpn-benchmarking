import json
import os.path
from pathlib import Path

from SingleGraphGenerator import *
from ValueType import *


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

    def generate_different_graphs(self, detailed_full: [bool, bool], normal_median: [bool, bool]):
        if detailed_full == [False, False] or normal_median == [False, False]:
            return

        if detailed_full[0] and normal_median[0]:
            self.generate_graphs(False, False)

        if detailed_full[0] and normal_median[1]:
            self.generate_graphs(False, True)

        if detailed_full[1] and normal_median[0]:
            self.generate_graphs(True, False)

        if detailed_full[1] and normal_median[1]:
            self.generate_graphs(True, True)
