import json
import os.path
from pathlib import Path

import dateutil.parser

from src.output.PlotGenerator import *
from src.output.ValueType import *


def validate_data(data, file_name: str) -> bool:
    """
    Checks if the given data has the correct format in all entries. Uses the file name only for more specific errors.
    :param data: data to be checked
    :param file_name: name of the file from which the data was extracted, only used for more specific errors
    :return: True for success, False otherwise
    """

    def check_data_fields():
        """
        Checks if there is only one field 'data', and if there are values in that field.
        :return: raises KeyError if check was not successful
        """
        if len(data) != 1 or not isinstance(data["data"], list):
            raise KeyError

        if len(data["data"]) < 1:
            raise KeyError

    def check_dictionary_size():
        """
        Checks if the dictionary is of type dictionary, and its length of 4 fields (name, timestamp, hardware and
        network)
        :return: raises KeyError if check was not successful
        """
        if not isinstance(dictionary, dict) or len(dictionary) != 4:
            raise KeyError

    def check_hardware_values():
        """
        Checks if the hardware fields in an entry are of correct types and length.
        :return: raises KeyError if check was not successful
        """
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
        """
        Checks if the network fields in an entry are of correct types and length.
        :return: raises KeyError if check was not successful
        """
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
        """
        Checks if the timestamp has the correct ISO format. Raises an error otherwise.
        """
        dateutil.parser.isoparse(dictionary["time"])

    def check_name():
        """
        Checks if the name is a string.
        :return: raises KeyError if check was not successful
        """
        if not isinstance(dictionary["name"], str):
            raise KeyError

    try:
        check_data_fields()

        for dictionary in data["data"]:
            check_dictionary_size()
            check_hardware_values()
            check_network_values()
            check_timestamp()
            check_name()

        return True
    except KeyError:
        print_warn(f"File {file_name} has incorrect or no data!")
        return False
    except ValueError:
        print_warn(f"File {file_name} has incorrect timestamp format!")
        return False
    except Exception as err:
        print(f"{err=}")
        return False


def get_single_timestamp(data, n: int):
    """
    Returns a single timestamp at position n in data.
    :param data: data in which the timestamp is located
    :param n: position in the list of timestamps
    :return: timestamp extracted from the data
    """
    return data["data"][n]["time"]


class SingleFileGraphHandler:
    """
    Handles the creation of graphs for one given input file.
    """

    def __init__(self, file_path, value_types: list) -> None:
        """
        Initializes the value_types, checks if the path is a JSON file, extracts path and name information. Also loads
        data from the file.
        :param file_path: path of the file to generate graphs for
        :param value_types: list of ValueTypes for which a graph should be generated
        """
        self.value_lists = {}
        self.value_types = value_types

        if not os.path.isfile(file_path):
            print_warn(f"{file_path} is not a file.")
            raise FileNotFoundError

        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        if self.file_name[-5:] != ".json":
            print_warn(f"{file_path} is not a JSON file.")
            raise FileNotFoundError
        self.short_file_name = self.file_name[:-5]

        if not self.__load_data_from_file():
            raise Exception("Unable to load data from file!")
        if not self.__fill_lists_from_data():
            raise Exception(f"Incorrect data format in {self.file_path}")

    def generate_graphs(self, full: bool, median: bool):
        """
        Generates the graphs for the file with fixed full and median booleans.
        :param full: True if y-limit is 0 to 100 percent for relative ValueType, False for detailed scope
        :param median: True if min-max-median graph should be generated, False for normal graphs
        """

        def calculate_full_time() -> float:
            """
            Calculates the full time the exchange took.
            :return: float of the full duration in seconds
            """
            initial_time = dateutil.parser.isoparse(self.value_lists["time"][0])
            last_time = dateutil.parser.isoparse(self.value_lists["time"][len(self.value_lists["time"]) - 1])
            return (last_time - initial_time).total_seconds()

        graph_dir_path = os.path.join("data_graphs", self.short_file_name)

        for value_type in self.value_types:
            name_string = value_type.get_name_string(value_type)
            category_string = value_type.get_category_string(value_type)

            title = self.__get_title(value_type, calculate_full_time(), median)

            generator = PlotGenerator(
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

    @staticmethod
    def __generate_filename(value_type, full: bool, median: bool) -> str:
        """
        Returns the file name of the final graph picture. A folder with all these pictures includes the files

        - normal.png
        - full.png
        - min-max-median.png
        - full_min-max-median.png.

        For absolute ValueTypes, only normal or min-max-median will be output.
        :param value_type: ValueType that was used for graph generation. Used to determine if full graphs are relevant.
        :param full: True if full option was used, False otherwise
        :param median: True if median option was used, False otherwise
        :return: filename of the picture as a string
        """
        if issubclass(value_type, RelativeValueType):
            if full and median:
                return "full_min-max-median"
            if full:
                return "full"

        if median:
            return "min-max-median"

        return "normal"

    def __save_figure(self, file_path, file_name):
        """
        Saves the before plotted graph(s) in a file. Cleans up afterward. Creates the necessary directories if needed.
        Prints log messages before and after.
        :param file_path: path to generate, put the file in this directory
        :param file_name: name of the file
        """
        print_log(f"Saving file {file_name}...")

        Path(file_path).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(file_path, file_name))
        plt.clf()
        self.__clean_up()

        print_log("File saved.")

    def __get_title(self, value_type, full_time: float, median: bool) -> str:
        """
        Returns the title that will be set in the figure. If the filename has the correct format, the title
        has the format:

        {value_type} (VPN: {vpn}) ({role}, {full_time} s) [(min/max/median)]

        If the title has an unknown format, the title will be set to:

        {value_type} ({full_time} s) [(min/max/median)]
        :param value_type: ValueType used in the graph
        :param full_time: full duration of the exchange pictured in the graph as float in seconds
        :param median: True if it is a min-max-median graph, False otherwise
        :return: title for the figure as string
        """

        def check_filename_format() -> bool:
            """
            Checks the format of the filename. Correct format is

            {role}-{vpn}_{year}-{month}-{day}T{hour}_{minute}_{second}.{second_parts}.
            :return: True if check was successful, False otherwise
            """
            tmp_split_name = self.short_file_name.split("_")

            if len(tmp_split_name) != 4:
                return False

            role_and_vpn_option = tmp_split_name[0]

            try:
                # replace the '_' with ':'
                dateutil.parser.isoparse(
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
            """
            Extracts the file name without '.json', splits it up into role and vpn.
            :return: tuple of role and vpn
            """
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
        """
        Opens the file, and loads the data from the file into self.data.
        :return: True for success, False otherwise
        """
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
        """
        Fills the classes lists of values from the loaded data. Validates data first.
        :return: True for success, False otherwise
        """
        if not validate_data(self.data, self.file_name):
            return False

        self.value_lists["time"] = []
        for i in range(len(self.data["data"])):
            # add timestamp entry
            self.value_lists["time"].append(get_single_timestamp(self.data, i))

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

    def __clean_up(self):
        """
        Resets the dictionary of lists to an empty dictionary. Loads the data again.
        :return:
        """
        self.value_lists = {}

        if not self.__load_data_from_file():
            raise Exception("Unable to load data from file!")
        if not self.__fill_lists_from_data():
            raise Exception(f"Incorrect data format in {self.file_path}")


class MultiFileGraphHandler:
    """
    Handles the creation of graphs for multiple given input files in the form of a directory or a single file.
    """

    def __init__(self, path, value_types: list) -> None:
        """
        Checks if the path is a file or directory.
        :param path: path of the file or directory to generate graphs for
        :param value_types: list of ValueTypes for which graphs should be generated
        """

        if not (os.path.isdir(path) or os.path.isfile(path)):
            print_warn(f"{path} is not a valid path.")
            return

        self.path = path
        self.value_types = value_types

    def generate_graphs(self, full: bool, median: bool):
        """
        Generates the graphs by calling the SingleFileGraphHandler for each file. Also prints log messages.
        :param full: True if y-limit is 0 to 100 percent for relative ValueType, False for detailed scope
        :param median: True if min-max-median graph should be generated, False for normal graphs
        """
        print_log("Start generating graphs...")
        if os.path.isdir(self.path):
            for file_name in os.listdir(self.path):
                single_file_handler = SingleFileGraphHandler(os.path.join(self.path, file_name), self.value_types)
                single_file_handler.generate_graphs(full, median)

                del single_file_handler
        elif os.path.isfile(self.path):
            single_file_handler = SingleFileGraphHandler(os.path.join(self.path), self.value_types)
            single_file_handler.generate_graphs(full, median)

            del single_file_handler
        else:
            raise ValueError
        print_log("Graphs generated.")
