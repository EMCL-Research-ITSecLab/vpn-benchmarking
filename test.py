import matplotlib.pyplot as plt
import numpy as np
 
 
# Creating dataset
# np.random.seed(10)
# # data = np.random.normal(100, 20, 200)
# data = np.array([1, 2, 3, 4, 5])
# print(data)
 
# fig = plt.figure(figsize =(10, 7))
 
# Creating plot
# plt.boxplot(data)

import matplotlib.pyplot as plt
import numpy as np
 
 
# Creating dataset
np.random.seed(10)
 
data_1 = np.array([1,2,3,4])
data_2 = np.array([2,3,4,5])
data_3 = np.array([3,4,5,6])
data_4 = np.array([3,4,5,6,7])
data = [data_1, data_2, data_3, data_4]
 
fig = plt.figure(figsize =(10, 7))
plt.ylim([0, 8])
 
# Creating plot
plt.boxplot(data, labels=["[0, 0.2]","[0.2, 0.4]","[0.4, 0.6]","[0.6, 0.8]"])

plt.savefig(".")