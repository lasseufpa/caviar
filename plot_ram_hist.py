import numpy as np
import matplotlib

matplotlib.use("pgf")
matplotlib.rcParams.update(
    {
        "pgf.texsystem": "pdflatex",
        "font.family": "serif",
        "text.usetex": True,
        "pgf.rcfonts": False,
    }
)
matplotlib.rc("xtick", labelsize=8)
matplotlib.rc("ytick", labelsize=8)
from matplotlib import pyplot as plt
import seaborn as sns

colors = sns.color_palette("deep")

sns.set_theme()

simode = "nowait"
n_bins = 50


one_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_1uavs_nowait_airsim.txt"
)
one_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_1uavs_nowait_mobility.txt"
)
one_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_1uavs_nowait_sionna.txt"
)
one_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_1uavs_nowait_nats.txt"
)

two_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_2uavs_nowait_airsim.txt"
)
two_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_2uavs_nowait_mobility.txt"
)
two_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_2uavs_nowait_sionna.txt"
)
two_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_2uavs_nowait_nats.txt"
)

three_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_3uavs_nowait_airsim.txt"
)
three_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_3uavs_nowait_mobility.txt"
)
three_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_3uavs_nowait_sionna.txt"
)
three_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_3uavs_nowait_nats.txt"
)

four_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_4uavs_nowait_airsim.txt"
)
four_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_4uavs_nowait_mobility.txt"
)
four_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_4uavs_nowait_sionna.txt"
)
four_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_4uavs_nowait_nats.txt"
)

five_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_5uavs_nowait_airsim.txt"
)
five_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_5uavs_nowait_mobility.txt"
)
five_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_5uavs_nowait_sionna.txt"
)
five_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_5uavs_nowait_nats.txt"
)


def moving_average(x, w):
    return np.convolve(x, np.ones(w), "valid") / w


def readFromFile(filepath):
    with open(filepath) as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    return line_array


unreal_one = np.array(readFromFile(one_uav_unreal_data_filepath), dtype=float)
unreal_two = np.array(readFromFile(two_uav_unreal_data_filepath), dtype=float)
unreal_three = np.array(readFromFile(three_uav_unreal_data_filepath), dtype=float)
unreal_four = np.array(readFromFile(four_uav_unreal_data_filepath), dtype=float)
unreal_five = np.array(readFromFile(five_uav_unreal_data_filepath), dtype=float)

airsim_one = np.array(readFromFile(one_uav_airsim_data_filepath), dtype=float)
airsim_two = np.array(readFromFile(two_uav_airsim_data_filepath), dtype=float)
airsim_three = np.array(readFromFile(three_uav_unreal_data_filepath), dtype=float)
airsim_four = np.array(readFromFile(four_uav_unreal_data_filepath), dtype=float)
airsim_five = np.array(readFromFile(five_uav_airsim_data_filepath), dtype=float)

yolo_one = np.array(readFromFile(one_uav_yolo_data_filepath), dtype=float)
yolo_two = np.array(readFromFile(two_uav_yolo_data_filepath), dtype=float)
yolo_three = np.array(readFromFile(three_uav_unreal_data_filepath), dtype=float)
yolo_four = np.array(readFromFile(four_uav_unreal_data_filepath), dtype=float)
yolo_five = np.array(readFromFile(five_uav_yolo_data_filepath), dtype=float)

ns3_one = np.array(readFromFile(one_uav_ns3_data_filepath), dtype=float)
ns3_two = np.array(readFromFile(two_uav_ns3_data_filepath), dtype=float)
ns3_three = np.array(readFromFile(three_uav_unreal_data_filepath), dtype=float)
ns3_four = np.array(readFromFile(four_uav_unreal_data_filepath), dtype=float)
ns3_five = np.array(readFromFile(five_uav_ns3_data_filepath), dtype=float)

unreal_one_cpu = unreal_one[:, 1]
unreal_two_cpu = unreal_two[:, 1]
unreal_three_cpu = unreal_three[:, 1]
unreal_four_cpu = unreal_four[:, 1]
unreal_five_cpu = unreal_five[:, 1]
unreal_one_ram = unreal_one[:, 2]
unreal_two_ram = unreal_two[:, 2]
unreal_three_ram = unreal_three[:, 2]
unreal_four_ram = unreal_four[:, 2]
unreal_five_ram = unreal_five[:, 2]

airsim_one_cpu = airsim_one[:, 1]
airsim_two_cpu = airsim_two[:, 1]
airsim_three_cpu = airsim_three[:, 1]
airsim_four_cpu = airsim_four[:, 1]
airsim_five_cpu = airsim_five[:, 1]
airsim_one_ram = airsim_one[:, 2]
airsim_two_ram = airsim_two[:, 2]
airsim_three_ram = airsim_three[:, 2]
airsim_four_ram = airsim_four[:, 2]
airsim_five_ram = airsim_five[:, 2]

yolo_one_cpu = yolo_one[:, 1]
yolo_two_cpu = yolo_two[:, 1]
yolo_three_cpu = yolo_three[:, 1]
yolo_four_cpu = yolo_four[:, 1]
yolo_five_cpu = yolo_five[:, 1]
yolo_one_ram = yolo_one[:, 2]
yolo_two_ram = yolo_two[:, 2]
yolo_three_ram = yolo_three[:, 2]
yolo_four_ram = yolo_four[:, 2]
yolo_five_ram = yolo_five[:, 2]

ns3_one_cpu = ns3_one[:, 1]
ns3_two_cpu = ns3_two[:, 1]
ns3_three_cpu = ns3_three[:, 1]
ns3_four_cpu = ns3_four[:, 1]
ns3_five_cpu = ns3_five[:, 1]
ns3_one_ram = ns3_one[:, 2]
ns3_two_ram = ns3_two[:, 2]
ns3_three_ram = ns3_three[:, 2]
ns3_four_ram = ns3_four[:, 2]
ns3_five_ram = ns3_five[:, 2]

plt.figure()
plt.xlabel("CPU (%)")
plt.ylabel("Number of occurrences")
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# plt.ylim(0, 90)
plt.hist(
    unreal_one_cpu,
    bins=n_bins,
    label="One UAV",
    color=colors[0],
    alpha=0.5,
)
plt.hist(
    unreal_two_cpu,
    bins=n_bins,
    label="Two UAVs",
    color=colors[1],
    alpha=0.5,
)
plt.hist(
    unreal_three_cpu,
    bins=n_bins,
    label="Three UAVs",
    color=colors[2],
    alpha=0.5,
)
plt.hist(
    unreal_four_cpu,
    bins=n_bins,
    label="Four UAVs",
    color=colors[3],
    alpha=0.5,
)
plt.hist(
    unreal_five_cpu,
    bins=n_bins,
    label="Five UAVs",
    color=colors[4],
    alpha=0.5,
)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/home/joao/Downloads/caviar_records/unreal_cpu_hist.pdf")
plt.close()

plt.figure()
plt.xlabel("CPU (%)")
plt.ylabel("Number of occurrences")
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# plt.ylim(0, 90)
plt.hist(
    airsim_one_cpu,
    bins=n_bins,
    label="One UAV",
    color=colors[0],
    alpha=0.5,
)
plt.hist(
    airsim_two_cpu,
    bins=n_bins,
    label="Two UAVs",
    color=colors[1],
    alpha=0.5,
)
plt.hist(
    airsim_three_cpu,
    bins=n_bins,
    label="Three UAVs",
    color=colors[2],
    alpha=0.5,
)
plt.hist(
    airsim_four_cpu,
    bins=n_bins,
    label="Four UAVs",
    color=colors[3],
    alpha=0.5,
)
plt.hist(
    airsim_five_cpu,
    bins=n_bins,
    label="Five UAVs",
    color=colors[4],
    alpha=0.5,
)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/home/joao/Downloads/caviar_records/airsim_cpu_hist.pdf")
plt.close()

plt.figure()
plt.xlabel("CPU (%)")
plt.ylabel("Number of occurrences")
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# plt.ylim(0, 90)
plt.hist(yolo_one_cpu, bins=n_bins, label="One UAV", color=colors[0], alpha=0.5)
plt.hist(
    yolo_two_cpu,
    bins=n_bins,
    label="Two UAVs",
    color=colors[1],
    alpha=0.5,
)
plt.hist(
    yolo_three_cpu,
    bins=n_bins,
    label="Three UAVs",
    color=colors[2],
    alpha=0.5,
)
plt.hist(
    yolo_four_cpu,
    bins=n_bins,
    label="Four UAVs",
    color=colors[3],
    alpha=0.5,
)
plt.hist(
    yolo_five_cpu,
    bins=n_bins,
    label="Five UAVs",
    color=colors[4],
    alpha=0.5,
)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/home/joao/Downloads/caviar_records/yolo_cpu_hist.pdf")
plt.close()

plt.figure()
plt.xlabel("CPU (%)")
plt.ylabel("Number of occurrences")
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# plt.ylim(0, 90)
plt.hist(ns3_one_cpu, bins=n_bins, label="One UAV", color=colors[0], alpha=0.5)
plt.hist(ns3_two_cpu, bins=n_bins, label="Two UAVs", color=colors[1], alpha=0.5)
plt.hist(
    ns3_three_cpu,
    bins=n_bins,
    label="Three UAVs",
    color=colors[2],
    alpha=0.5,
)
plt.hist(
    ns3_four_cpu,
    bins=n_bins,
    label="Four UAVs",
    color=colors[3],
    alpha=0.5,
)
plt.hist(
    ns3_five_cpu,
    bins=n_bins,
    label="Five UAVs",
    color=colors[4],
    alpha=0.5,
)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/home/joao/Downloads/caviar_records/ns3_cpu_hist.pdf")
plt.close()

# ---------------------------------------------------------------------------

plt.figure()
plt.xlabel("Memory (MB)")
plt.ylabel("Number of occurrences")
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# plt.ylim(0, 90)
plt.hist(
    unreal_one_ram,
    bins=n_bins,
    label="One UAV",
    color=colors[0],
    alpha=0.5,
)
plt.hist(
    unreal_two_ram,
    bins=n_bins,
    label="Two UAVs",
    color=colors[1],
    alpha=0.5,
)
plt.hist(
    unreal_three_ram,
    bins=n_bins,
    label="Three UAVs",
    color=colors[2],
    alpha=0.5,
)
plt.hist(
    unreal_four_ram,
    bins=n_bins,
    label="Four UAVs",
    color=colors[3],
    alpha=0.5,
)
plt.hist(
    unreal_five_ram,
    bins=n_bins,
    label="Five UAVs",
    color=colors[4],
    alpha=0.5,
)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/home/joao/Downloads/caviar_records/unreal_ram_hist.pdf")
plt.close()

plt.figure()
plt.xlabel("Memory (MB)")
plt.ylabel("Number of occurrences")
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# plt.ylim(0, 90)
plt.hist(
    airsim_one_ram,
    bins=n_bins,
    label="One UAV",
    color=colors[0],
    alpha=0.5,
)
plt.hist(
    airsim_two_ram,
    bins=n_bins,
    label="Two UAVs",
    color=colors[1],
    alpha=0.5,
)
plt.hist(
    airsim_three_ram,
    bins=n_bins,
    label="Three UAVs",
    color=colors[2],
    alpha=0.5,
)
plt.hist(
    airsim_four_ram,
    bins=n_bins,
    label="Four UAVs",
    color=colors[3],
    alpha=0.5,
)
plt.hist(
    airsim_five_ram,
    bins=n_bins,
    label="Five UAVs",
    color=colors[4],
    alpha=0.5,
)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/home/joao/Downloads/caviar_records/airsim_ram_hist.pdf")
plt.close()

plt.figure()
plt.xlabel("Memory (MB)")
plt.ylabel("Number of occurrences")
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# plt.ylim(0, 90)
plt.hist(yolo_one_ram, bins=n_bins, label="One UAV", color=colors[0], alpha=0.5)
plt.hist(
    yolo_two_ram,
    bins=n_bins,
    label="Two UAVs",
    color=colors[1],
    alpha=0.5,
)
plt.hist(
    yolo_three_ram,
    bins=n_bins,
    label="Three UAVs",
    color=colors[2],
    alpha=0.5,
)
plt.hist(
    yolo_four_ram,
    bins=n_bins,
    label="Four UAVs",
    color=colors[3],
    alpha=0.5,
)
plt.hist(
    yolo_five_ram,
    bins=n_bins,
    label="Five UAVs",
    color=colors[4],
    alpha=0.5,
)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/home/joao/Downloads/caviar_records/yolo_ram_hist.pdf")
plt.close()

plt.figure()
plt.xlabel("Memory (MB)")
plt.ylabel("Number of occurrences")
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# plt.ylim(0, 90)
plt.hist(ns3_one_ram, bins=n_bins, label="One UAV", color=colors[0], alpha=0.5)
plt.hist(ns3_two_ram, bins=n_bins, label="Two UAVs", color=colors[1], alpha=0.5)
plt.hist(
    ns3_three_ram,
    bins=n_bins,
    label="Three UAVs",
    color=colors[2],
    alpha=0.5,
)
plt.hist(
    ns3_four_ram,
    bins=n_bins,
    label="Four UAVs",
    color=colors[3],
    alpha=0.5,
)
plt.hist(
    ns3_five_ram,
    bins=n_bins,
    label="Five UAVs",
    color=colors[4],
    alpha=0.5,
)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("/home/joao/Downloads/caviar_records/ns3_ram_hist.pdf")
plt.close()
