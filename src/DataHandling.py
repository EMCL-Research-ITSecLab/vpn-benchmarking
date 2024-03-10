import datetime
import json
from json import JSONEncoder
from pathlib import Path


class DataHandling:
    """
    Handles all data operations for storing and writing data to a file.
    """
    data = {"data": []}  # for storing data from the file

    def __init__(self, role, vpn) -> None:
        """
        Gets timestamp for now, creates data directory and sets part of the name format.
        :param role: role of the host, needed for file name
        :param vpn: VPN used for the exchange, needed for file name
        """
        self.timestamp = datetime.datetime.now().isoformat()
        self.name = f"{role}-{vpn}"
        Path("data").mkdir(parents=True, exist_ok=True)

    def write_data(self) -> None:
        """
        Creates and/or opens the file and writes the data from the internal data structure to the JSON file.

        File name consists of the name (role-vpn), '_' and the timestamp in ISO format (but with '_' instead of ':' for
        compatibility reasons). File is created in 'data' directory.
        """
        timestamp = self.timestamp.replace(":", "_")

        with open(f"data/{self.name}_{timestamp}.json", "w") as file:
            json.dump(
                self.data,  # data to be stored in the file
                indent=2,  # indent used for the lines
                sort_keys=True,  # sorts the keys by alphabet
                fp=file,  # file to be used
                cls=DateTimeEncoder  # format of the data
            )

    def add_data(
            self, name, time, cpu_perc, ram_perc, pps_sent, pps_recv, bytes_sent, bytes_recv
    ) -> None:
        """
        Adds the given data fields to an internal data structure. Format of the information is split up into name,
        timestamp, hardware values and network values.
        :param name: short description of the situation in which the poll was created
        :param time: timestamp of the poll
        :param cpu_perc: relative CPU usage value
        :param ram_perc: relative RAM usage value
        :param pps_sent: sent packets per second value
        :param pps_recv: received packets per second value
        :param bytes_sent: sent amount of bytes since beginning
        :param bytes_recv: received amount of bytes since beginning
        """
        new_data = {
            "name": name,
            "time": time,
            "hardware": [
                {
                    "cpu_percent": cpu_perc,
                    "ram_percent": ram_perc
                }
            ],
            "network": [
                {
                    "pps_sent": pps_sent,
                    "pps_recv": pps_recv,
                    "bytes_sent": bytes_sent,
                    "bytes_recv": bytes_recv,
                }
            ],
        }

        self.data["data"].append(new_data)


class DateTimeEncoder(JSONEncoder):
    """
    Specifies the JSON format.
    """

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
