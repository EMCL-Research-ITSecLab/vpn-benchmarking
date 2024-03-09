import datetime
import threading
import time

import psutil

from src.DataHandling import DataHandling


class Monitoring:
    """
    Handles the monitoring of performance parameters. Runs several processes for updating values.
    """
    done = threading.Event()  # signals to subprocesses if monitoring has stopped

    def __init__(self, role, vpn) -> None:
        """
        Creates an instance for handling data (storing and writing) and initializes starting values.
        :param role: role of the host, needed for file name of data file
        :param vpn: VPN used, needed for file name of data file
        """
        self.monitor = None
        self.interval = None
        self.data_handler = DataHandling(role, vpn)

        self.initial_bytes_sent = psutil.net_io_counters().bytes_sent
        self.initial_bytes_recv = psutil.net_io_counters().bytes_recv
        self.pps_sent, self.pps_recv = 0, 0

    def start(self, auto=True, interval=0.1) -> None:
        """
        Starts the monitoring and necessary threads for the updating values. Polls can happen automatically
        repeatedly after a specified interval. Automatic polls start when this is executed. Manual polls are possible
        as soon as this method was executed.
        :param auto: True (default) for automatic polls every [interval] seconds, False for only manual polls
        :param interval: interval for automatic polls in seconds
        """
        self.interval = interval

        pps_sent = threading.Thread(target=self.__update_packets_per_second_sent)
        pps_recv = threading.Thread(target=self.__update_packets_per_second_recv)

        pps_sent.start()
        pps_recv.start()

        if auto:
            self.monitor = threading.Thread(target=self.__updating_poll)
            self.monitor.start()

    def stop(self) -> None:
        """
        Stops the monitoring and signals all threads to stop. Automatic polls stop, manual polls are not
        possible after calling this method. Signals the data handler to store the collected information in a file.
        """
        self.done.set()
        self.data_handler.write_data()

    def poll(self, name) -> None:
        """
        Does a manual poll. Sends current measurement data to the data handler.
        :param name: short description of the situation in which the poll was created
        """
        self.data_handler.add_data(
            name=name,
            time=datetime.datetime.now(),
            cpu_perc=self.__get_cpu_percent(),
            ram_perc=self.__get_ram_percent(),
            pps_sent=self.pps_sent,
            pps_recv=self.pps_recv,
            bytes_sent=self.__get_upload_bytes(),
            bytes_recv=self.__get_download_bytes(),
        )

    def __updating_poll(self) -> None:
        """
        Repeatedly does automatic polls after the specified interval. Stops when 'done' is set. Names of automatic
        polls are set to 'automatic poll'.
        """
        while not self.done.is_set():
            self.data_handler.add_data(
                name="automatic poll",
                time=datetime.datetime.now(),
                cpu_perc=self.__get_cpu_percent(),
                ram_perc=self.__get_ram_percent(),
                pps_sent=self.pps_sent,
                pps_recv=self.pps_recv,
                bytes_sent=self.__get_upload_bytes(),
                bytes_recv=self.__get_download_bytes(),
            )
            time.sleep(self.interval)

    @staticmethod
    def __get_cpu_percent():
        """
        :return: current relative CPU usage in percent
        """
        return psutil.cpu_percent()

    @staticmethod
    def __get_ram_percent():
        """
        :return: current relative RAM usage in percent
        """
        return psutil.virtual_memory()[2]

    def __get_upload_bytes(self):
        """
        :return: difference of amount of upload bytes since start
        """
        return psutil.net_io_counters().bytes_sent - self.initial_bytes_sent

    def __get_download_bytes(self):
        """
        :return: difference of amount of download bytes since start
        """
        return psutil.net_io_counters().bytes_recv - self.initial_bytes_recv

    def __update_packets_per_second_sent(self):
        """
        Continuously calculates the packets per second (sent) value by using the specified interval.
        :return: sent packets per second in the last interval
        """
        while not self.done.is_set():
            before = psutil.net_io_counters().packets_sent
            time.sleep(self.interval)
            self.pps_sent = int(
                (psutil.net_io_counters().packets_sent - before) / self.interval
            )

    def __update_packets_per_second_recv(self):
        """
        Continuously calculates the packets per second (received) value by using the specified interval.
        :return: received packets per second in the last interval
        """
        while not self.done.is_set():
            before = psutil.net_io_counters().packets_recv
            time.sleep(self.interval)
            self.pps_recv = int(
                (psutil.net_io_counters().packets_recv - before) / self.interval
            )
