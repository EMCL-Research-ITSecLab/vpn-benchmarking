#!/usr/bin/env python3

import curses
import psutil
import threading
import time


global interval
interval = 0.5


class Screen:	
    def __init__(self) -> None:  
        self.win = curses.initscr()
    
        curses.noecho()
        curses.cbreak()
        self.win.keypad(True)
  
    def __del__(self) -> None:
        curses.nocbreak()
        self.win.keypad(False)
        curses.echo()
        curses.endwin()
    
    
class Monitoring:
    done = threading.Event()
    
    def __init__(self) -> None:
        self.scr = Screen()
        self.cpu_percent = self.HardwareValue(psutil.cpu_times_percent, 0)
        self.ram_percent = self.HardwareValue(psutil.virtual_memory, 2)
        self.initial_bytes_sent = psutil.net_io_counters().bytes_sent
        self.initial_bytes_recv = psutil.net_io_counters().bytes_recv
    
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
            
            # Hardware Performance
            printscr(0, 1, f"Performance:")
            printscr(2, 2, f"CPU:")
            printscr(2, 10, f"{self.cpu_percent.get()} %     ")
            printscr(3, 2, f"RAM:")
            printscr(3, 10, f"{self.ram_percent.get()} %     ")
            
            # Network Performance
            printscr(0, 30, f"Network:")
            printscr(2, 31, f"PPS:")
            printscr(2, 42, f"TODO packets per second")         # TODO: Add implementation
            printscr(3, 31, f"Upload:")
            printscr(3, 42, f"{self.__format_bytes(self.__get_upload_bytes())}     ")
            printscr(4, 31, f"Download:")
            printscr(4, 42, f"{self.__format_bytes(self.__get_download_bytes())}     ")
            
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
        
    def __get_packets_per_second():
        # TODO: Implement
        pass
    
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
                
        
# only for testing purposes     
def test():
    i = 0
    for _ in range(499999999):
        i += 1
        
    
if __name__ == "__main__":
    monitor = Monitoring()
    monitor.run(test)
    