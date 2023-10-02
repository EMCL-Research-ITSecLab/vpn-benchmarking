import logging
import threading
import time

import psutil


class Monitoring:
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    done = threading.Event()
    CUT_OFF = 1

    def run(self, func):
        logging.info(f"starting monitoring")

        monitor = threading.Thread(target=self.__updating_values)
        target = threading.Thread(target=func)
        monitor.start()
        target.start()

        while target.is_alive():
            time.sleep(0.5)

        self.done.set()

        logging.info("monitoring completed")

    def __updating_values(self):
        cpu_percent_sum = 0
        ram_percent_sum = 0
        pre_iterations = 1
        iterations = 1
        
        while not self.done.is_set():
            cpu_percent = self.__get_cpu_percent()
            ram_percent = self.__get_ram_percent()
            print(f"CPU: {cpu_percent} %     RAM: {ram_percent} %", end="     \r")
            
            if pre_iterations > self.CUT_OFF:
                cpu_percent_sum += cpu_percent
                ram_percent_sum += ram_percent
                iterations += 1
            else:
                pre_iterations += 1
                
            time.sleep(0.5)
            
        cpu_percent_avrg = self.__average(cpu_percent_sum, iterations - self.CUT_OFF)   # TODO: Add check for negative values
        ram_percent_avrg = self.__average(ram_percent_sum, iterations - self.CUT_OFF)
        print(f"  CPU average: {cpu_percent_avrg} %\n  RAM average: {ram_percent_avrg} %")
            
    def __average(self, sum, iterations):
        return "{:4.1f}".format(sum / iterations)

    def __get_cpu_percent(self):
        return psutil.cpu_times_percent()[0]

    def __get_ram_percent(self):
        return psutil.virtual_memory()[2]


# only for testing purposes
def do_sth():
    i = 0
    for _ in range(99999999):
        i += 1


if __name__ == "__main__":
    monitor = Monitoring()
    monitor.run(do_sth)
