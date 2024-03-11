from src.messages import *


def get_smallest_bytes_unit(n):
    """
    Returns the smallest unit for a given bytes amount. For example, KiB or MiB.
    :param n: number of bytes
    :return: most readable unit for the given bytes amount, for example 3.45 MiB.
    """
    for unit in ["", "K", "M", "G", "T", "P"]:
        if n < 1024:
            if unit == "":
                return "B"
            else:
                return f"{unit}iB"
        n = n / 1024
    print_err("Number of bytes is too large!")


class ValueType:
    """
    Base class for all the types of values, used by the graph generator to get names as well as labels and limits.
    """

    def __init__(self, values: list, full: bool, median: bool) -> None:
        """
        Sets the parameters from the arguments and calculates the number of values as self.length.
        :param values: list of values of that ValueType
        :param full: True if full graph is generated, False otherwise
        :param median: True if min-max-median graph is generated, False otherwise
        """
        self.values = values
        self.length = len(values)
        self.full = full
        self.median = median

    def get_category_string(self):
        """
        Returns the name of the category of the ValueType, for example 'hardware'. Base implementation raises
        NotImplementedError.
        """
        print_err("ValueType.get_category_string(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_name_string(self):
        """
        Returns the technical name of the ValueType, for example 'cpu_percent'. Base implementation raises
        NotImplementedError.
        """
        print_err("ValueType.get_name_string(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_description(self):
        """
        Returns the technical name of the ValueType, for example 'cpu_percent'. Base implementation raises
        NotImplementedError.
        """
        print_err("ValueType.get_description(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_x_label(self, interval_length=None) -> str:
        """
        Returns the x-label for the graph. For min-max-median graphs, this is the number of time interval, for all
        others it is the time in seconds.
        :param interval_length: length of one interval, only used for min-max-median graphs
        :return: x-label as string
        """
        if self.median:
            return "#time interval (of length {:.3f} s)".format(interval_length)

        return "time [s]"

    def get_y_label(self):
        """
        Returns the y-label. Base implementation raises NotImplementedError.
        """
        print_err("ValueType.get_y_label(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_x_limit(self, max_value) -> list:
        """
        Returns the x-limits. For min-max-median graphs, raises ValueError, since x-limit is automatically set.
        :param max_value: maximum value in the list of used values for the graph
        :return: list of min_value and max_value
        """
        if not self.median:
            return [0, max_value]

        print_err("x-limit for median graphs is automatically set.")
        raise ValueError

    def get_y_limit(self):
        """
        Returns the y-limits. Base implementation raises NotImplementedError.
        """
        print_err("ValueType.get_y_limit(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_adjusted_values(self) -> list:
        """
        If needed, can be used to adjust the values (e.g. to a different unit). Simply returns unchanged values in
        base implementation.
        :return: list of adjusted values
        """
        return self.values


class RelativeValueType(ValueType):
    """
    Implementation of relative ValueTypes, meaning those given as percentage values.
    """

    def get_y_limit(self) -> list:
        """
        Returns the y-limits. If full is set, these are 0 and 100, otherwise they are calculated so that a useful part
        of the scope of values is shown.
        :return: list of min and max limit
        """
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
    """
    Implementation of absolute ValueTypes.
    """

    def get_y_limit(self) -> list | None:
        """
        Returns the y-limits. If max is 0 or not set, returns None
        :return: list of min and max limit or None
        """
        if not max(self.values):
            return None
        return [0, 1.05 * max(self.values)]


class CPUPercent(RelativeValueType):
    """
    Implements the CPU usage in percent.
    """

    def get_name_string(self) -> str:
        """
        :return: 'cpu_percent'
        """
        return "cpu_percent"

    def get_category_string(self) -> str:
        """
        :return: 'hardware'
        """
        return "hardware"

    def get_description(self) -> str:
        """
        :return: 'CPU usage'
        """
        return "CPU usage"

    def get_y_label(self) -> str:
        """
        :return: 'CPU usage [%]'
        """
        return "CPU usage [%]"


class RAMPercent(RelativeValueType):
    """
    Implements the RAM usage in percent.
    """

    def get_name_string(self) -> str:
        """
        :return: 'ram_percent'
        """
        return "ram_percent"

    def get_category_string(self) -> str:
        """
        :return: 'hardware'
        """
        return "hardware"

    def get_description(self) -> str:
        """
        :return: 'RAM usage'
        """
        return "RAM usage"

    def get_y_label(self) -> str:
        """
        :return: 'RAM usage [%]'
        """
        return "RAM usage [%]"


class RecvBytes(AbsoluteValueType):
    """
    Implements the total amount of received bytes.
    """

    def get_name_string(self) -> str:
        """
        :return: 'bytes_recv'
        """
        return "bytes_recv"

    def get_category_string(self) -> str:
        """
        :return: 'network'
        """
        return "network"

    def get_description(self) -> str:
        """
        :return: 'Total received bytes'
        """
        return "Total received bytes"

    def get_y_label(self) -> str:
        """
        Calculates smallest unit and returns y-label.
        :return: 'total bytes (received) [{unit}]'
        """
        unit = get_smallest_bytes_unit(max(self.values))
        return f"total bytes (received) [{unit}]"

    def get_adjusted_values(self) -> list:
        """
        Adjusts the values to fit to the calculated smallest unit.
        :return: list of adjusted values
        """
        values = self.values

        while max(values) > 1024:
            for v in range(len(values)):
                values[v] = values[v] / 1024

        return values


class SentBytes(AbsoluteValueType):
    """
    Implements the total amount of sent bytes.
    """

    def get_name_string(self) -> str:
        """
        :return: 'bytes_sent'
        """
        return "bytes_sent"

    def get_category_string(self) -> str:
        """
        :return: 'network'
        """
        return "network"

    def get_description(self) -> str:
        """
        :return: 'Total sent bytes'
        """
        return "Total sent bytes"

    def get_y_label(self) -> str:
        """
        Calculates smallest unit and returns y-label.
        :return: 'total bytes (sent) [{unit}]'
        """
        unit = get_smallest_bytes_unit(max(self.values))
        return f"total bytes (sent) [{unit}]"

    def get_adjusted_values(self) -> list:
        """
        Adjusts the values to fit to the calculated smallest unit.
        :return: list of adjusted values
        """
        values = self.values

        while max(values) > 1024:
            for v in range(len(values)):
                values[v] = values[v] / 1024

        return values


class RecvPPS(AbsoluteValueType):
    """
    Implements the received packets per second.
    """

    def get_name_string(self) -> str:
        """
        :return: 'pps_recv'
        """
        return "pps_recv"

    def get_category_string(self) -> str:
        """
        :return: 'network'
        """
        return "network"

    def get_description(self) -> str:
        """
        :return: 'Received PPS'
        """
        return "Received PPS"

    def get_y_label(self) -> str:
        """
        :return: 'packets per second (received)'
        """
        return "packets per second (received)"


class SentPPS(AbsoluteValueType):
    """
    Implements the sent packets per second.
    """

    def get_name_string(self) -> str:
        """
        :return: 'pps_sent'
        """
        return "pps_sent"

    def get_category_string(self) -> str:
        """
        :return: 'network'
        """
        return "network"

    def get_description(self) -> str:
        """
        :return: 'Sent PPS'
        """
        return "Sent PPS"

    def get_y_label(self) -> str:
        """
        :return: 'packets per second (sent)'
        """
        return "packets per second (sent)"
