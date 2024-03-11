import os

from src.GraphHandler import *
from src.messages import *


class DataOutput:
    """
    Base class for different types of data outputs. An implementation can use the data from a file and generate some
    kind of visualization from it, like graphs, tables or charts.
    """

    def generate(self):
        """
        Generates the visual representation. Throws a NotImplementedError in base implementation.
        """
        print_err("DataOutput.generate(self): NOT IMPLEMENTED")
        raise NotImplementedError


class GraphOutput(DataOutput):
    """
    Implements the graph output.
    """

    def __init__(self, path: str, value_types: list, detailed_full: [bool, bool], normal_median: [bool, bool]):
        """
        Checks if at least one of the detailed, full and normal, median pairs of booleans is True, otherwise raises
        ValueError. Checks if path exists, otherwise throws FileNotFoundError. Sets the parameters.
        :param path: path of a directory if JSON files with correct format or a single JSON file
        :param value_types: list of value_types to generate graphs for
        :param detailed_full: a pair of booleans, first stands for generate detailed graphs, second for full graphs
        :param normal_median: a pair of booleans, first stands for generate normal graphs, second for min-max-median
        graphs
        """
        if detailed_full == [False, False] or normal_median == [False, False]:
            raise ValueError

        if not os.path.exists(path):
            raise FileNotFoundError

        self.path = path
        self.value_types = value_types
        self.detailed_full = detailed_full
        self.normal_median = normal_median

    def generate(self):
        """
        Implements the generation for graphs. Creates a MultiFileGraphHandler with the initial parameters, goes through
        all combinations of input pairs and generates respective graphs.
        """
        generator = MultiFileGraphHandler(self.path, self.value_types)

        if self.detailed_full[0] and self.normal_median[0]:
            generator.generate_graphs(False, False)

        if self.detailed_full[0] and self.normal_median[1]:
            generator.generate_graphs(False, True)

        if self.detailed_full[1] and self.normal_median[0]:
            generator.generate_graphs(True, False)

        if self.detailed_full[1] and self.normal_median[1]:
            generator.generate_graphs(True, True)
