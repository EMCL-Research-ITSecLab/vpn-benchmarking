import json
import matplotlib.pyplot as plt 

list = []

with open("data/data:2023-11-09T11:05:48.739616.json") as file:
    data = json.load(file)

for i in range(len(data["data"])):
    list.append(data["data"][i]["hardware"][0]["cpu_percent"])
    
plt.plot(list)
plt.show()
plt.savefig("new")