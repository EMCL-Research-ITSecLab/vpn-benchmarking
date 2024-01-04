import psutil
import threading
import time
import datetime

from DataHandling import DataHandling


class Monitoring:
    done = threading.Event()

    def __init__(self, name) -> None:
        self.data_handler = DataHandling(name)

        self.initial_bytes_sent = psutil.net_io_counters().bytes_sent
        self.initial_bytes_recv = psutil.net_io_counters().bytes_recv
        self.pps_sent, self.pps_recv = 0, 0

    def start(self, auto=True, interval=0.1):
        self.interval = interval

        pps_sent = threading.Thread(target=self.__update_packets_per_second_sent)
        pps_recv = threading.Thread(target=self.__update_packets_per_second_recv)

        pps_sent.start()
        pps_recv.start()

        if auto == True:
            self.monitor = threading.Thread(target=self.__updating_poll)
            self.monitor.start()

    def stop(self):
        self.done.set()
        self.data_handler.write_data()

    def poll(self, name):
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

    def __updating_poll(self):
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

    def __get_cpu_percent(self):
        return psutil.cpu_percent()

    def __get_ram_percent(self):
        return psutil.virtual_memory()[2]

    def __get_upload_bytes(self):
        return psutil.net_io_counters().bytes_sent - self.initial_bytes_sent

    def __get_download_bytes(self):
        return psutil.net_io_counters().bytes_recv - self.initial_bytes_recv

    def __update_packets_per_second_sent(self):
        while not self.done.is_set():
            before = psutil.net_io_counters().packets_sent
            time.sleep(self.interval)
            self.pps_sent = int(
                (psutil.net_io_counters().packets_sent - before) / self.interval
            )

    def __update_packets_per_second_recv(self):
        while not self.done.is_set():
            before = psutil.net_io_counters().packets_recv
            time.sleep(self.interval)
            self.pps_recv = int(
                (psutil.net_io_counters().packets_recv - before) / self.interval
            )
