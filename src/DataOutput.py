import os

from src.GraphHandler import *
from src.messages import *


class DataOutput:
    def generate(self):
        print_err("DataOutput.generate(self): NOT IMPLEMENTED")
        raise NotImplementedError


class GraphOutput(DataOutput):
    def __init__(self, path: str, value_types: list, detailed_full: [bool, bool], normal_median: [bool, bool]):
        if detailed_full == [False, False] or normal_median == [False, False]:
            return

        if not os.path.exists(path):
            raise FileNotFoundError

        self.path = path
        self.value_types = value_types
        self.detailed_full = detailed_full
        self.normal_median = normal_median

    def generate(self):
        generator = MultiFileGraphHandler(self.path, self.value_types)

        if self.detailed_full[0] and self.normal_median[0]:
            generator.generate_graphs(False, False)

        if self.detailed_full[0] and self.normal_median[1]:
            generator.generate_graphs(False, True)

        if self.detailed_full[1] and self.normal_median[0]:
            generator.generate_graphs(True, False)

        if self.detailed_full[1] and self.normal_median[1]:
            generator.generate_graphs(True, True)
