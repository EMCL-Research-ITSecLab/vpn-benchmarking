import matplotlib.pyplot as plt
import numpy as np

x = np.array([0,1,4,9,16,25,36,49])
y = np.array([0,1,2,3,4,5,6,7])

plt.plot(x, y, color='r')
# plt.plot(y, color='g')

plt.xlabel("Test")
plt.ylabel("Other")

plt.xlim([0, max(x)+0.5])
plt.ylim([0, max(y)+0.5])

plt.savefig("test")