import psutil
import threading
import time
import datetime

from DataHandling import DataHandling


global interval
interval = 0.1
    
    
class Monitoring:
    done = threading.Event()
    
    def __init__(self, folder_name) -> None:
        self.data_handler = DataHandling(folder_name)
        
        self.cpu_percent = self.HardwareValue(psutil.cpu_times_percent, 0)
        self.ram_percent = self.HardwareValue(psutil.virtual_memory, 2)
        self.initial_bytes_sent = psutil.net_io_counters().bytes_sent
        self.initial_bytes_recv = psutil.net_io_counters().bytes_recv
        self.pps_sent = 0
        self.pps_recv = 0
    
    def start(self, auto=True):
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
            cpu_perc=self.cpu_percent.get(), 
            ram_perc=self.ram_percent.get(), 
            pps_sent=self.pps_sent, 
            pps_recv=self.pps_recv, 
            bytes_sent=self.__get_upload_bytes(), 
            bytes_recv=self.__get_download_bytes()
        )
        
    def __updating_poll(self):
        while not self.done.is_set():
            self.data_handler.add_data(
                name="automatic poll",
                time=datetime.datetime.now(), 
                cpu_perc=self.cpu_percent.get(), 
                ram_perc=self.ram_percent.get(), 
                pps_sent=self.pps_sent, 
                pps_recv=self.pps_recv, 
                bytes_sent=self.__get_upload_bytes(), 
                bytes_recv=self.__get_download_bytes()
            )
            time.sleep(interval)
         
    # might be useful for later
    def __format_bytes(self, bytes):
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}B     "
            bytes = bytes / 1024  
    
    def __get_upload_bytes(self):
        return psutil.net_io_counters().bytes_sent - self.initial_bytes_sent
    
    def __get_download_bytes(self):
        return psutil.net_io_counters().bytes_recv - self.initial_bytes_recv
        
    def __update_packets_per_second_sent(self):
        while not self.done.is_set():
            before = psutil.net_io_counters().packets_sent
            time.sleep(interval)
            self.pps_sent = int((psutil.net_io_counters().packets_sent - before) / interval)
            
    def __update_packets_per_second_recv(self):
        while not self.done.is_set():
            before = psutil.net_io_counters().packets_recv
            time.sleep(interval)
            self.pps_recv = int((psutil.net_io_counters().packets_recv - before) / interval)
        
    
    class HardwareValue:
        cut_off = 1     # number of cycles to ignore for average calculation
        
        def __init__(self, func, attr) -> None:
            self.function = func
            self.attribute = attr
            self.sum = 0
            self.iterations = 1 - self.cut_off
            
        def get(self):
            value = self.function()[self.attribute]
            
            if self.iterations >= 1:
                self.sum += value
                
            self.iterations += 1
            
            return value
        
        def get_average(self):
            if self.iterations < 1:
                return "{:4.1f}".format(0)
            else:
                return "{:4.1f}".format(self.sum / self.iterations)
        