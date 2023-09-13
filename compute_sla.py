import numpy as np
from joblib import load

approach = "dec_tree"  # Choose between "oracle", "dec_tree" or "random"

latency_package_size = 64

run = np.load("no-rescue_mission_set.npz")

rx_current_positions = run["rx_current_position"]
bit_rate_Gbps = run["bit_rate"] * 1e-9

clf = load("trained_model_v7.joblib")
enc = load("trained_encoder_v7.joblib")

all_predicted_bit_rate_Gbps = []
for idx, rx_current_position in enumerate(rx_current_positions):
    pred_beam_index = enc.inverse_transform(
        clf.predict(np.array([rx_current_position]))
    )[0][1:-1].split(",")
    predicted_bit_rate_Gbps = bit_rate_Gbps[
        idx, int(pred_beam_index[0]), int(pred_beam_index[1])
    ]
    all_predicted_bit_rate_Gbps.append(predicted_bit_rate_Gbps)

data = []

if approach == "oracle":
    data = run["best_bit_rate_Gbps"]
elif approach == "dec_tree":
    data = all_predicted_bit_rate_Gbps
else:
    data = run["random_bit_rate_Gbps"]


def get_latency(package_size, throughput):
    """
    This function calculates the time for transmit them all and finish
    the rescue.

    The rescue will finish after transmiting 100 pictures of 4 MB (3.2e7 bits), representing
    a 4K image and a point cloud file made with LiDAR with 2 GB (16e9 bits)
    """
    data_to_transmit_in_bits = package_size * 8
    latency = data_to_transmit_in_bits / (throughput * 1e9)
    return latency


def compute_throughput_sla(throughput_list, throughput_sla):
    success = 0
    throughput_slis = []
    for idx, throughput in enumerate(throughput_list):
        if throughput >= throughput_sla:
            success += 1
        throughput_slis.append((success / (idx + 1)) * 100)
    return throughput_slis


def compute_latency_sla(latency_list, latency_sla):
    success = 0
    latency_slis = []
    for idx, latency in enumerate(latency_list):
        if get_latency(latency_package_size, latency) <= latency_sla:
            success += 1
        latency_slis.append((success / (idx + 1)) * 100)
    return latency_slis


throughput_slis = []
throughput_slas = np.arange(0.01, 0.1, 0.01)
for sla in throughput_slas:
    throughput_slis.append(compute_throughput_sla(data, sla))

latency_slis = []
latency_slas = np.arange(0, 0.2, 0.01)
latency_slas[0] = 0.001
for sla in latency_slas:
    latency_slis.append(compute_latency_sla(data, sla))


import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

# ------------------ Throughput -----------------------------------

ax = plt.figure().add_subplot(projection="3d")

for idx, sli in enumerate(throughput_slis):
    ax.plot(range(len(sli)), sli, zs=(throughput_slas[idx] * 1e3))

ax.legend()
ax.set_xlabel("Time steps")
ax.set_ylabel("SLI adherence (%)")
ax.view_init(elev=90, azim=-90, roll=0)
ax.set_zlabel("Throughput SLA (Mbps)")
ax.set_ylim(0, 100)
plt.title(f"Throughput ({approach})")
plt.savefig(f"SLI_throughput_{approach}.png")

# ------------------ Latency -----------------------------------

ax = plt.figure().add_subplot(projection="3d")

for idx, sli in enumerate(latency_slis):
    ax.plot(range(len(sli)), sli, zs=(latency_slas[idx] * 1e3))

ax.legend()
ax.set_xlabel("Time steps")
ax.set_ylabel("SLI adherence (%)")
ax.view_init(elev=90, azim=-90, roll=0)
ax.set_zlabel("Latency SLA (ms)")
ax.set_ylim(0, 100)
plt.title(f"Latency ({approach})")
plt.savefig(f"SLI_latency_{approach}.png")
