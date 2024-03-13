import dateutil.parser
import matplotlib.pyplot as plt

from src.messages import *


class PlotGenerator:
    """
    Plots a graph from given data.
    """

    def __init__(self, value_type, timestamps: list, values: list, full: bool, median: bool, title: str = "") -> None:
        """
        Checks if timestamps and values are consistent regarding number of entries. Sets all parameters from arguments.
        :param value_type: ValueType to plot the graph for
        :param timestamps: timestamps to be used for the x-axis
        :param values: values to be used for the graph
        :param full: True if y-limit is 0 to 100 percent for relative ValueType, False for detailed scope
        :param median: True if min-max-median graph should be plotted, False for normal graphs
        :param title: title for the figure as string
        """
        if not len(timestamps) == len(values):
            raise ValueError

        self.value_instance = value_type(values, full, median)
        self.timestamps = timestamps
        self.values = values
        self.full = full
        self.median = median
        self.title = title

    def plot_graph(self):
        """
        Prepares plotting by setting basic settings, labels, limits and title. Calls plot method, also prints log
        messages.
        """
        print_log("Plotting graph...")

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
        print_log("Graph plotted.")

    def __plot(self, values):
        """
        Plots the data. Distinguishes between min-max-median graphs and normal graphs.
        :param values: values to plot
        """
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
        :return: list of absolute timestamps as floats starting from 0.0
        """
        timestamps = [0.0]
        initial_time = dateutil.parser.isoparse(self.timestamps[0])

        for i in range(1, len(self.timestamps)):
            cur_time = dateutil.parser.isoparse(self.timestamps[i])
            timestamps.append((cur_time - initial_time).total_seconds())

        return timestamps

    @staticmethod
    def __adjust_basic_plot_settings():
        """
        Sets the basic settings for the plot environment.
        """
        plt.grid(True, "both", "y")  # turn on y-axis grid
        plt.minorticks_on()  # turn on ticks

    def __partition_data(self, initial_data, number_blocks=8):
        """
        Partitions the data into multiple blocks. Used only for min-max-median graphs.
        :param initial_data: data before separation into blocks
        :param number_blocks: number of blocks, 8 by default
        """

        def calculate_block_number():
            """
            Calculates in which block a value with its timestamp belongs.
            :return:
            """
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
        """
        Sets the title of the plot.
        """
        plt.title(self.title, fontweight="bold", fontsize=9)

    @staticmethod
    def __set_x_label(text):
        """
        Sets the x-label of the plot to text.
        :param text: x-label text
        """
        plt.xlabel(text)

    @staticmethod
    def __set_y_label(text):
        """
        Sets the y-label of the plot to text.
        :param text: y-label text
        """
        plt.ylabel(text)

    @staticmethod
    def __set_x_limit(limits: list):
        """
        Sets the x-limit of the plot to the two values given in limits.
        :param limits: list of the two x-limits (min- and max-limit)
        """
        plt.xlim(limits)

    @staticmethod
    def __set_y_limit(limits: list):
        """
        Sets the y-limit of the plot to the two values given in limits if not both are 0.
        :param limits: list of the two y-limits (min- and max-limit)
        """
        if limits:
            plt.ylim(limits)
