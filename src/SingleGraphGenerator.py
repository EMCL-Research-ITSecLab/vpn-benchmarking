from datetime import datetime

import matplotlib.pyplot as plt
from src.messages import *


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

    @staticmethod
    def __adjust_basic_plot_settings():
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
        Sets the y-limit of the plot to the two values given in limits.
        :param limits: list of the two y-limits (min- and max-limit)
        """
        if limits:
            plt.ylim(limits)
