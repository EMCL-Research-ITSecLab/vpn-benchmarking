import pathlib

import click
import inquirer

from src.output.DataOutput import *


class HandleInput:
    """
    Handles the inputs given.
    """
    valid_inputs = False

    def __init__(
            self, output_type, path, full, detailed, median, normal
    ) -> None:
        """
        Sets all values to the given inputs and checks the values.
        :param output_type: type of the output, for example as 'graphs'
        :param path: path of the file or directory of the data
        :param full: True if full graphs should be generated, False otherwise
        :param detailed: True if detailed graphs should be generated, False otherwise
        :param median: True if median graphs should be generated, False otherwise
        :param normal: True if normal graphs should be generated, False otherwise
        """
        self.type = output_type
        self.path = path
        self.full = full
        self.detailed = detailed
        self.median = median
        self.normal = normal

        if self.__check_values():
            self.valid_inputs = True

    def execute(self, value_types: list):
        """
        If inputs are valid, generates the output with the respective class.
        :return: True for success, False otherwise
        """
        if self.type == "graphs":
            output = GraphOutput(
                self.path,
                value_types,
                [self.detailed, self.full],
                [self.normal, self.median]
            )
            output.generate()

    def __check_values(self) -> bool:
        """
        Checks if the given inputs are in the defined scope. Returns False otherwise.
        :return: True for success, False otherwise
        """
        if not self.type == "graphs":
            print_err(
                "Invalid TYPE argument. Has to be graphs."
            )
            return False

        if not os.path.exists(self.path):
            print_err(
                "Invalid PATH argument. Has to be an existent directory or file."
            )
            return False

        if not (self.detailed or self.full):
            print_err(
                "Either --detailed, --full or both must be set."
            )
            return False

        if not (self.normal or self.median):
            print_err(
                "Either --normal, --median or both must be set."
            )
            return False

        return True


@click.command()
@click.option("-f", "--full", help="generate relative graphs from 0 to 100 percent", is_flag=True)
@click.option("-d", "--detailed", help="generate relative graphs in the relevant scope", is_flag=True)
@click.option("-m", "--median", help="generate min-max-median graphs", is_flag=True)
@click.option("-n", "--normal", help="generate normal graphs", is_flag=True)
@click.argument("output_type", type=str)
@click.argument("path", type=pathlib.Path)
def cli(output_type, path, full, detailed, median, normal):
    """
    Takes arguments from the command line, asks the user for the values for which graphs should be generated and
    calls the InputHandler with the arguments and user inputs.

    With output_type, the user can specify which kind of output he wants to generate. The output_type 'graphs' uses
    the flags -f, -d, -m and -n to limit the scope of what graphs should be generated. The pairs -f, -d and -n, -m
    specify the y-limits and the type of graph, 'normal' graphs with all values or min-max-median graphs with 8
    intervals, respectively. At least one option of each pair has to be set, possibly both. All different combinations
    that are checked create a graph, for example if flags -f, -d and -m are set, the program generates full and detailed
    min-max-median graphs, but no 'normal' graphs.
    :param output_type: type of the output, for example as 'graphs'
    :param path: path of the file or directory of the data
    :param full: True if full graphs should be generated, False otherwise
    :param detailed: True if detailed graphs should be generated, False otherwise
    :param median: True if median graphs should be generated, False otherwise
    :param normal: True if normal graphs should be generated, False otherwise
    """
    questions = [
        inquirer.Checkbox(
            "values",
            message="Choose value types to create graphs for",
            choices=[
                "all",
                "CPU usage (%)",
                "RAM usage (%)",
                "Total received bytes",
                "Total sent bytes",
                "Received packets per second",
                "Sent packets per second",
            ],
        ),
    ]

    answers = inquirer.prompt(questions)

    if not answers:
        print_err("Something went wrong!")
        return

    all_set = "all" in answers["values"]
    cpu_usage = "CPU usage (%)" in answers["values"]
    ram_usage = "RAM usage (%)" in answers["values"]
    recv_bytes = "Total received bytes" in answers["values"]
    sent_bytes = "Total sent bytes" in answers["values"]
    recv_pps = "Received packets per second" in answers["values"]
    sent_pps = "Sent packets per second" in answers["values"]

    value_types = []

    if cpu_usage or all_set:
        value_types.append(CPUPercent)
    if ram_usage or all_set:
        value_types.append(RAMPercent)
    if recv_bytes or all_set:
        value_types.append(RecvBytes)
    if sent_bytes or all_set:
        value_types.append(SentBytes)
    if recv_pps or all_set:
        value_types.append(RecvPPS)
    if sent_pps or all_set:
        value_types.append(SentPPS)

    handler = HandleInput(output_type, path, full, detailed, median, normal)
    handler.execute(value_types)


if __name__ == "__main__":
    cli()
