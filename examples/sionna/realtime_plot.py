
import numpy as np
import matplotlib.pyplot as plt


# Just to set a fixed value for the axes: (xmin, xmax, ymin, ymax)
# plt.axis([0, 10, 0, 1])

plt.figure()
plt.title("Throughputs (Gbps)")
global mean_line1
global mean_line2
global mean_line3

mean_line1 = plt.axhline(y=0, color="blue")
mean_line2 = plt.axhline(y=0, color="green")
mean_line3 = plt.axhline(y=0, color="red")

# Inspired by Velimir Mlaker answer available at
# https://stackoverflow.com/questions/11874767/how-do-i-plot-in-real-time-in-a-while-loop
# CC BY-SA 4.0
def plot_throughput(timestamp, throughput1, throughput2, throughput3, mean1, mean2, mean3, mean_line1=mean_line1, mean_line2=mean_line2, mean_line3=mean_line3):
    plt.scatter(timestamp, throughput1, color="blue")
    plt.scatter(timestamp, throughput2, color="green")
    plt.scatter(timestamp, throughput3, color="red", marker=".") 
    mean_line1.set_ydata(mean1)
    mean_line2.set_ydata(mean2)
    mean_line3.set_ydata(mean3)
    plt.legend([f"Optimal | mean: {round(mean1, 2)}", f"Predicted | mean: {round(mean2, 2)}", f"Random | mean: {round(mean3, 2)}"], loc="upper left")
    plt.pause(0.05)


if __name__ == "__main__":
    all_throughput1 = []
    all_throughput2 = []
    all_throughput3 = []
    for timestamp in range(10):
        throughput1 = np.random.random()
        throughput2 = np.random.random()
        throughput3 = np.random.random()
        all_throughput1.append(throughput1)
        all_throughput2.append(throughput2)
        all_throughput3.append(throughput3)
        mean1 = np.mean(all_throughput1)
        mean2 = np.mean(all_throughput2)
        mean3 = np.mean(all_throughput3)
        plot_throughput(timestamp, throughput1, throughput2, throughput3, mean1, mean2, mean3)
        plt.legend(["Optimal", "Predicted", "Random"], loc="upper left")

    plt.show()