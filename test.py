from DataOutput import DataOutput
import datetime
from Monitoring import Monitoring


output = DataOutput(
    cpu_percent=True,
    ram_percent=True,
    bytes_recv=True,
    bytes_sent=True,
    pps_recv=True,
    pps_sent=True,
)

# make_graphs_for_directory
# # test: file not a directory
# output.make_graphs_for_directory("hosts.json", False, False)

# # test: directory does not exist
# output.make_graphs_for_directory("does_not_exist", False, False)

# # test: directory exists but does not contain json files
# output.make_graphs_for_directory("test_dir", False, False)

# # test: directory exists and contains only incorrect json files
# output.make_graphs_for_directory("test_dir2", False, False)


# make_graphs_for_file
# # test: directory not a file
# output.make_graphs_for_file("test_dir", False, False)

# # test: file does not exist
# output.make_graphs_for_file("does_not_exist.json", False, False)

# # test: incorrect json file
# output.make_graphs_for_file("test_dir2/false.json", False, False)

# print(datetime.datetime.now().isoformat())

# output.check_file_name_and_set_attributes("client-novpn:2024-01-04T12:29:19.843495.json")

import psutil

monitor = Monitoring("test-novpn")

monitor.start(auto=True)
### start test
for i in range(99999999):
    i += i
### end test
monitor.stop()
