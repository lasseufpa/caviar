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
    data_to_transmit_in_bits = 3.2e7 * 10
    time_to_tx = data_to_transmit_in_bits / (throughput)
    return time_to_tx


if __name__ == "__main__":
    throughputs = np.arange(1, 100, 0.1)
    # throughputs = np.arange(20, 100, 0.1)
    rescue_times = []
    for throughput in throughputs:
        throughput_bps = throughput * 1e6
        rescue_times.append(get_time_for_rescue(throughput_bps))

    sns.set_theme()
    plt.figure(figsize=(7, 6))
    plt.plot(throughputs, rescue_times)
    plt.grid(True)

    x_ticks = np.arange(0, 101, 5)
    x_ticks[0] = 1

    y_ticks = np.arange(0, 351, 15)

    plt.xticks(x_ticks)
    plt.yticks(y_ticks)
    plt.xlim(0.75, 100)
    plt.ylim(-1, 325)
    plt.xlabel("Throughput (Mbps)")
    plt.ylabel("Estimated virtual time to finish one rescue (seconds)")
    plt.tight_layout()
    plt.savefig("time_to_finish_rescues_mbps.pdf")
