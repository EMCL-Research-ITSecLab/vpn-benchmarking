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
    
    def run(self, func):
        monitor = threading.Thread(target=self.poll)
        target = threading.Thread(target=func)
        monitor.start()
        target.start()
        
        while target.is_alive():
            time.sleep(interval)
            
        self.done.set()
        
    def poll(self):
        while not self.done.is_set():
            # Hardware Performance
            self.scr.win.addstr(0, 1, f"Performance:")
            self.scr.win.addstr(2, 2, f"CPU:")
            self.scr.win.addstr(2, 10, f"{self.cpu_percent.get()} %")
            self.scr.win.addstr(3, 2, f"RAM:")
            self.scr.win.addstr(3, 10, f"{self.ram_percent.get()} %")
            
            # Network Performance
            self.scr.win.addstr(0, 30, f"Network:")
            self.scr.win.addstr(2, 31, f"PPS:")
            self.scr.win.addstr(2, 42, f"TODO packets per second")  # TODO: Add implementation
            self.scr.win.addstr(3, 31, f"Upload:")
            self.scr.win.addstr(3, 42, f"TODO Bytes")               # TODO: Add implementation
            self.scr.win.addstr(4, 31, f"Download:")
            self.scr.win.addstr(4, 42, f"TODO Bytes")               # TODO: Add implementation
            
            self.scr.win.refresh()
            time.sleep(interval)
        
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
    
    #class NetworkValue:
        
        # TODO: Add implementation
                
        
# only for testing purposes     
def test():
    i = 0
    for _ in range(499999999):
        i += 1
        
    
if __name__ == "__main__":
    monitor = Monitoring()
    monitor.run(test)
    