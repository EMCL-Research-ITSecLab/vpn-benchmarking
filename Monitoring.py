import psutil
import threading
import time

from Screen import Screen


global interval
interval = 0.5
    
    
class Monitoring:
    done = threading.Event()
    
    def __init__(self) -> None:
        self.scr = Screen()
        self.cpu_percent = self.HardwareValue(psutil.cpu_times_percent, 0)
        self.ram_percent = self.HardwareValue(psutil.virtual_memory, 2)
        self.initial_bytes_sent = psutil.net_io_counters().bytes_sent
        self.initial_bytes_recv = psutil.net_io_counters().bytes_recv
        self.pps_sent = 0
        self.pps_recv = 0
    
    def run(self, func):
        monitor = threading.Thread(target=self.__poll)
        target = threading.Thread(target=func)
        monitor.start()
        target.start()
        
        while target.is_alive():
            time.sleep(interval)
            
        self.done.set()
        
    def __poll(self):
        while not self.done.is_set():
            printscr = lambda a, b, str : self.scr.win.addstr(a, b, str)
            pps_sent = threading.Thread(target=self.__update_packets_per_second_sent)
            pps_recv = threading.Thread(target=self.__update_packets_per_second_recv)
            
            pps_sent.start()
            pps_recv.start()
            
            # Hardware Performance
            printscr(0, 1, f"Performance:")
            printscr(2, 2, f"CPU:")
            printscr(2, 10, f"{self.cpu_percent.get()} %     ")
            printscr(3, 2, f"RAM:")
            printscr(3, 10, f"{self.ram_percent.get()} %     ")
            
            # Network Performance
            printscr(0, 30, f"Network:")
            printscr(2, 31, f"PPS (sent):")
            printscr(2, 50, f"{self.pps_sent} packets per second     ")
            printscr(3, 31, f"PPS (received):")
            printscr(3, 50, f"{self.pps_recv} packets per second     ")
            printscr(4, 31, f"Upload:")
            printscr(4, 50, f"{self.__format_bytes(self.__get_upload_bytes())}     ")
            printscr(5, 31, f"Download:")
            printscr(5, 50, f"{self.__format_bytes(self.__get_download_bytes())}     ")
            
            self.scr.win.refresh()
            time.sleep(interval)
            
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
        