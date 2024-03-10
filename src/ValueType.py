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

    def get_category_string(self):
        messages.print_err("ValueType.get_category_string(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_name_string(self):
        messages.print_err("ValueType.get_name_string(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_description(self):
        messages.print_err("ValueType.get_description(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_x_label(self, interval_length=None) -> str:
        if self.median:
            return "#time interval (of length {:.3f} s)".format(interval_length)

        return "time [s]"

    def get_y_label(self):
        messages.print_err("ValueType.get_y_label(self): NOT IMPLEMENTED")
        raise NotImplementedError

    def get_x_limit(self, max_value) -> list:
        if not self.median:
            return [0, max_value]

        messages.print_err("x-limit for median graphs is automatically set.")
        raise ValueError

    def get_y_limit(self):
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
