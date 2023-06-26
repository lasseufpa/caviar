
import numpy as np
import matplotlib.pyplot as plt


# Just to set a fixed value for the axes: (xmin, xmax, ymin, ymax)
# plt.axis([0, 10, 0, 1])

plt.figure()
plt.title("Throughputs (Gbps)")


# Inspired by Velimir Mlaker answer available at
# https://stackoverflow.com/questions/11874767/how-do-i-plot-in-real-time-in-a-while-loop
# CC BY-SA 4.0
def plot_throughput(timestamp, throughput1, throughput2):
    plt.scatter(timestamp, throughput1, color="blue")
    plt.scatter(timestamp, throughput2, color="red")
    plt.pause(0.05)


# if __name__ == "__main__":
#     for timestamp in range(10):
#         throughput1 = np.random.random()
#         throughput2 = np.random.random()
#         plot_throughput(timestamp, throughput1, throughput2)
#         plt.legend(["Optimal", "Random"], loc="upper right")

#     plt.show()