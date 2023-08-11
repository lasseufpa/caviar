import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def get_time_for_rescue(throughput):
    """
    This function calculates the time for transmit them all and finish
    the rescue.

    The rescue will finish after transmiting 100 pictures of 4 MB (3.2e7 bits), representing
    a 4K image and a point cloud file made with LiDAR with 2 GB (16e9 bits)
    """
    data_to_transmit_in_bits = (3.2e7 * 100) + (16e9)
    time_to_tx = data_to_transmit_in_bits / (throughput)
    return time_to_tx


if __name__ == "__main__":
    # throughputs = np.arange(0, 100, 0.1)
    # throughputs = np.arange(15, 100, 0.1)
    throughputs = np.arange(0.2, 1.6, 0.1)
    rescue_times = []
    for throughput in throughputs:
        throughput_bps = throughput * 1e9
        rescue_times.append(get_time_for_rescue(throughput_bps))

    sns.set_theme()
    plt.plot(throughputs, rescue_times)
    plt.grid(True)
    plt.xlabel("Throughputs (Gbps)")
    plt.ylabel("Rescue times (seconds)")
    plt.savefig("time_to_finish_rescues.png")
