import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

colors = sns.color_palette("deep")
colors = [colors[1], colors[2], colors[3], colors[0], colors[4]]

sns.set_theme()

simode = "newgpu"
n_bins = 50

one_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_1uavs_newgpu_airsim.txt"
)
one_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_1uavs_newgpu_mobility.txt"
)
one_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_1uavs_newgpu_sionna.txt"
)
one_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_1uavs_newgpu_nats.txt"
)

two_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_2uavs_newgpu_airsim.txt"
)
two_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_2uavs_newgpu_mobility.txt"
)
two_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_2uavs_newgpu_sionna.txt"
)
two_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_2uavs_newgpu_nats.txt"
)

three_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_3uavs_newgpu_airsim.txt"
)
three_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_3uavs_newgpu_mobility.txt"
)
three_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_3uavs_newgpu_sionna.txt"
)
three_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_3uavs_newgpu_nats.txt"
)

four_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_4uavs_newgpu_airsim.txt"
)
four_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_4uavs_newgpu_mobility.txt"
)
four_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_4uavs_newgpu_sionna.txt"
)
four_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_4uavs_newgpu_nats.txt"
)

five_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_5uavs_newgpu_airsim.txt"
)
five_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_5uavs_newgpu_mobility.txt"
)
five_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_5uavs_newgpu_sionna.txt"
)
five_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_5uavs_newgpu_nats.txt"
)

ten_uav_unreal_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_10uavs_newgpu_airsim.txt"
)
ten_uav_airsim_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_10uavs_newgpu_mobility.txt"
)
ten_uav_yolo_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_10uavs_newgpu_sionna.txt"
)
ten_uav_ns3_data_filepath = (
    "/home/joao/Downloads/caviar_records/for_10uavs_newgpu_nats.txt"
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
unreal_ten = np.array(readFromFile(ten_uav_unreal_data_filepath), dtype=float)

airsim_one = np.array(readFromFile(one_uav_airsim_data_filepath), dtype=float)
airsim_two = np.array(readFromFile(two_uav_airsim_data_filepath), dtype=float)
airsim_three = np.array(readFromFile(three_uav_airsim_data_filepath), dtype=float)
airsim_four = np.array(readFromFile(four_uav_airsim_data_filepath), dtype=float)
airsim_five = np.array(readFromFile(five_uav_airsim_data_filepath), dtype=float)
airsim_ten = np.array(readFromFile(ten_uav_airsim_data_filepath), dtype=float)

yolo_one = np.array(readFromFile(one_uav_yolo_data_filepath), dtype=float)
yolo_two = np.array(readFromFile(two_uav_yolo_data_filepath), dtype=float)
yolo_three = np.array(readFromFile(three_uav_yolo_data_filepath), dtype=float)
yolo_four = np.array(readFromFile(four_uav_yolo_data_filepath), dtype=float)
yolo_five = np.array(readFromFile(five_uav_yolo_data_filepath), dtype=float)
yolo_ten = np.array(readFromFile(ten_uav_yolo_data_filepath), dtype=float)

ns3_one = np.array(readFromFile(one_uav_ns3_data_filepath), dtype=float)
ns3_two = np.array(readFromFile(two_uav_ns3_data_filepath), dtype=float)
ns3_three = np.array(readFromFile(three_uav_ns3_data_filepath), dtype=float)
ns3_four = np.array(readFromFile(four_uav_ns3_data_filepath), dtype=float)
ns3_five = np.array(readFromFile(five_uav_ns3_data_filepath), dtype=float)
ns3_ten = np.array(readFromFile(ten_uav_ns3_data_filepath), dtype=float)

# ------------------------------------------------------------------------------
unreal_one_cpu = unreal_one[:, 1] / 12
unreal_two_cpu = unreal_two[:, 1] / 12
unreal_three_cpu = unreal_three[:, 1] / 12
unreal_four_cpu = unreal_four[:, 1] / 12
unreal_five_cpu = unreal_five[:, 1] / 12
unreal_ten_cpu = unreal_ten[:, 1] / 12
unreal_one_ram = unreal_one[:, 2]
unreal_two_ram = unreal_two[:, 2]
unreal_three_ram = unreal_three[:, 2]
unreal_four_ram = unreal_four[:, 2]
unreal_five_ram = unreal_five[:, 2]
unreal_ten_ram = unreal_ten[:, 2]

unreal_cpus = [
    unreal_one_cpu,
    unreal_two_cpu,
    unreal_three_cpu,
    unreal_four_cpu,
    unreal_five_cpu,
    unreal_ten_cpu,
]

unreal_cpu_means = [np.mean(cpu) for cpu in unreal_cpus]
unreal_cpu_stds = [np.std(cpu) for cpu in unreal_cpus]

unreal_rams = [
    unreal_one_ram,
    unreal_two_ram,
    unreal_three_ram,
    unreal_four_ram,
    unreal_five_ram,
    unreal_ten_ram,
]
unreal_ram_means = [np.mean(ram) for ram in unreal_rams]
unreal_ram_stds = [np.std(ram) for ram in unreal_rams]

# ------------------------------------------------------------------------------
airsim_one_cpu = airsim_one[:, 1] / 12
airsim_two_cpu = airsim_two[:, 1] / 12
airsim_three_cpu = airsim_three[:, 1] / 12
airsim_four_cpu = airsim_four[:, 1] / 12
airsim_five_cpu = airsim_five[:, 1] / 12
airsim_ten_cpu = airsim_ten[:, 1] / 12
airsim_one_ram = airsim_one[:, 2]
airsim_two_ram = airsim_two[:, 2]
airsim_three_ram = airsim_three[:, 2]
airsim_four_ram = airsim_four[:, 2]
airsim_five_ram = airsim_five[:, 2]
airsim_ten_ram = airsim_ten[:, 2]

airsim_cpus = [
    airsim_one_cpu,
    airsim_two_cpu,
    airsim_three_cpu,
    airsim_four_cpu,
    airsim_five_cpu,
    airsim_ten_cpu,
]
airsim_cpu_means = [np.mean(cpu) for cpu in airsim_cpus]
airsim_cpu_stds = [np.std(cpu) for cpu in airsim_cpus]

airsim_rams = [
    airsim_one_ram,
    airsim_two_ram,
    airsim_three_ram,
    airsim_four_ram,
    airsim_five_ram,
    airsim_ten_ram,
]
airsim_ram_means = [np.mean(ram) for ram in airsim_rams]
airsim_ram_stds = [np.std(ram) for ram in airsim_rams]

# ------------------------------------------------------------------------------
yolo_one_cpu = yolo_one[:, 1] / 12
yolo_two_cpu = yolo_two[:, 1] / 12
yolo_three_cpu = yolo_three[:, 1] / 12
yolo_four_cpu = yolo_four[:, 1] / 12
yolo_five_cpu = yolo_five[:, 1] / 12
yolo_ten_cpu = yolo_ten[:, 1] / 12
yolo_one_ram = yolo_one[:, 2]
yolo_two_ram = yolo_two[:, 2]
yolo_three_ram = yolo_three[:, 2]
yolo_four_ram = yolo_four[:, 2]
yolo_five_ram = yolo_five[:, 2]
yolo_ten_ram = yolo_ten[:, 2]

yolo_cpus = [
    yolo_one_cpu,
    yolo_two_cpu,
    yolo_three_cpu,
    yolo_four_cpu,
    yolo_five_cpu,
    yolo_ten_cpu,
]
yolo_cpu_means = [np.mean(cpu) for cpu in yolo_cpus]
yolo_cpu_stds = [np.std(cpu) for cpu in yolo_cpus]

yolo_rams = [
    yolo_one_ram,
    yolo_two_ram,
    yolo_three_ram,
    yolo_four_ram,
    yolo_five_ram,
    yolo_ten_ram,
]
yolo_ram_means = [np.mean(ram) for ram in yolo_rams]
yolo_ram_stds = [np.std(ram) for ram in yolo_rams]


# ------------------------------------------------------------------------------
ns3_one_cpu = ns3_one[:, 1] / 12
ns3_two_cpu = ns3_two[:, 1] / 12
ns3_three_cpu = ns3_three[:, 1] / 12
ns3_four_cpu = ns3_four[:, 1] / 12
ns3_five_cpu = ns3_five[:, 1] / 12
ns3_ten_cpu = ns3_ten[:, 1] / 12
ns3_one_ram = ns3_one[:, 2]
ns3_two_ram = ns3_two[:, 2]
ns3_three_ram = ns3_three[:, 2]
ns3_four_ram = ns3_four[:, 2]
ns3_five_ram = ns3_five[:, 2]
ns3_ten_ram = ns3_ten[:, 2]

ns3_cpus = [
    ns3_one_cpu,
    ns3_two_cpu,
    ns3_three_cpu,
    ns3_four_cpu,
    ns3_five_cpu,
    ns3_ten_cpu,
]
ns3_cpu_means = [np.mean(cpu) for cpu in ns3_cpus]
ns3_cpu_stds = [np.std(cpu) for cpu in ns3_cpus]

ns3_rams = [
    ns3_one_ram,
    ns3_two_ram,
    ns3_three_ram,
    ns3_four_ram,
    ns3_five_ram,
    ns3_ten_ram,
]
ns3_ram_means = [np.mean(ram) for ram in ns3_rams]
ns3_ram_stds = [np.std(ram) for ram in ns3_rams]

# ------------------------------------------------------------------------------
total_cpu_means = []

for idx in [0, 1, 2, 3, 4, 5]:
    total_cpu_means.append(
        unreal_cpu_means[idx]
        + airsim_cpu_means[idx]
        + ns3_cpu_means[idx]
        + yolo_cpu_means[idx]
    )

total_cpu_stds = []

for idx in [0, 1, 2, 3, 4, 5]:
    total_cpu_stds.append(
        unreal_cpu_stds[idx]
        + airsim_cpu_stds[idx]
        + ns3_cpu_stds[idx]
        + yolo_cpu_stds[idx]
    )

total_ram_means = []

for idx in [0, 1, 2, 3, 4, 5]:
    total_ram_means.append(
        unreal_ram_means[idx]
        + airsim_ram_means[idx]
        + ns3_ram_means[idx]
        + yolo_ram_means[idx]
    )

total_ram_stds = []

for idx in [0, 1, 2, 3, 4, 5]:
    total_ram_stds.append(
        unreal_ram_stds[idx]
        + airsim_ram_stds[idx]
        + ns3_ram_stds[idx]
        + yolo_ram_stds[idx]
    )

# ------------------------------------------------------------------------------

# classes = ("One", "Two", "Three", "Four", "Five", "Ten")
classes = ("One", "Three", "Five", "Ten")
cpu_means = {
    "Mob+3D": (
        unreal_cpu_means[0],
        unreal_cpu_means[2],
        unreal_cpu_means[4],
        unreal_cpu_means[5],
    ),
    "AI": (
        airsim_cpu_means[0],
        airsim_cpu_means[2],
        airsim_cpu_means[4],
        airsim_cpu_means[5],
    ),
    "Orchestrator": (
        ns3_cpu_means[0],
        ns3_cpu_means[2],
        ns3_cpu_means[4],
        ns3_cpu_means[5],
    ),
    "Communications": (
        yolo_cpu_means[0],
        yolo_cpu_means[2],
        yolo_cpu_means[4],
        yolo_cpu_means[5],
    ),
    "Total": (
        total_cpu_means[0],
        total_cpu_means[2],
        total_cpu_means[4],
        total_cpu_means[5],
    ),
}

cpu_std_devs = {
    "Mob+3D": (
        unreal_cpu_stds[0],
        unreal_cpu_stds[2],
        unreal_cpu_stds[4],
        unreal_cpu_stds[5],
    ),
    "AI": (
        airsim_cpu_stds[0],
        airsim_cpu_stds[2],
        airsim_cpu_stds[4],
        airsim_cpu_stds[5],
    ),
    "Orchestrator": (
        ns3_cpu_stds[0],
        ns3_cpu_stds[2],
        ns3_cpu_stds[4],
        ns3_cpu_stds[5],
    ),
    "Communications": (
        yolo_cpu_stds[0],
        yolo_cpu_stds[2],
        yolo_cpu_stds[4],
        yolo_cpu_stds[5],
    ),
    "Total": (
        0,
        0,
        0,
        0,
    ),
}

ram_means = {
    "Mob+3D": (
        unreal_ram_means[0],
        unreal_ram_means[2],
        unreal_ram_means[4],
        unreal_ram_means[5],
    ),
    "AI": (
        airsim_ram_means[0],
        airsim_ram_means[2],
        airsim_ram_means[4],
        airsim_ram_means[5],
    ),
    "Orchestrator": (
        ns3_ram_means[0],
        ns3_ram_means[2],
        ns3_ram_means[4],
        ns3_ram_means[5],
    ),
    "Communications": (
        yolo_ram_means[0],
        yolo_ram_means[2],
        yolo_ram_means[4],
        yolo_ram_means[5],
    ),
    "Total": (
        total_ram_means[0],
        total_ram_means[2],
        total_ram_means[4],
        total_ram_means[5],
    ),
}

ram_std_devs = {
    "Mob+3D": (
        unreal_ram_stds[0],
        unreal_ram_stds[2],
        unreal_ram_stds[4],
        unreal_ram_stds[5],
    ),
    "AI": (
        airsim_ram_stds[0],
        airsim_ram_stds[2],
        airsim_ram_stds[4],
        airsim_ram_stds[5],
    ),
    "Orchestrator": (
        ns3_ram_stds[0],
        ns3_ram_stds[2],
        ns3_ram_stds[4],
        ns3_ram_stds[5],
    ),
    "Communications": (
        yolo_ram_stds[0],
        yolo_ram_stds[2],
        yolo_ram_stds[4],
        yolo_ram_stds[5],
    ),
    "Total": (
        0,
        0,
        0,
        0,
    ),
}

hatches = {
    "Mob+3D": "",
    "AI": "*",
    "Orchestrator": "-",
    "Communications": "/",
    "Total": "|",
}

x = np.arange(len(classes))
width = 0.15
multiplier = 0

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": "Times New Roman",
        "font.size": 20,
        "legend.fontsize": 28,
        "axes.labelsize": 34,
        "xtick.labelsize": 34,
        "ytick.labelsize": 34,
    }
)
fig, ax = plt.subplots(layout="constrained")
fig.set_figwidth(26)
fig.set_figheight(7)

for idx, ((attribute, measurement), std_dev, curr_hatch) in enumerate(
    zip(cpu_means.items(), cpu_std_devs.values(), hatches.values())
):
    offset = width * multiplier

    curr_color = colors[idx]

    # iterate over measurement array and truncate values to first three decimal values
    measurement = [np.trunc(val * 1000) / 1000 for val in measurement]

    # # iterate over measurement array and truncate values to first three decimal values
    # std_dev = [np.trunc(val * 1000) / 1000 for val in std_dev]

    rects = ax.bar(
        x + offset,
        measurement,
        width,
        hatch=curr_hatch,
        color=curr_color,
        label=attribute,
    )

    ax.bar_label(rects, padding=3)
    multiplier += 1

ax.set_ylabel("CPU (%)")
ax.set_xlabel("Number of UAVs")
ax.set_yticks(np.arange(0, 100 + 1, 10))
ax.set_xticks(x + width, classes)
ax.legend(loc="upper left", ncols=3)
ax.set_ylim(0, 100)
plt.savefig(
    "/home/joao/papers/2023-joaoborges-caviarrt-ieee-journal-dblcolumn/Figures/CPU.pdf"
)
plt.close()

# ------------------------------------------------------------------------------


x = np.arange(len(classes))
width = 0.15
multiplier = 0

fig, ax = plt.subplots(layout="constrained")
fig.set_figwidth(26)
fig.set_figheight(7)

for idx, ((attribute, measurement), std_dev, curr_hatch) in enumerate(
    zip(ram_means.items(), ram_std_devs.values(), hatches.values())
):
    offset = width * multiplier

    curr_color = colors[idx]

    # iterate over measurement array and truncate values to first three decimal values
    measurement = [np.trunc(val * 1000) / 1000 for val in measurement]

    rects = ax.bar(
        x + offset,
        measurement,
        width,
        hatch=curr_hatch,
        color=curr_color,
        label=attribute,
    )

    ax.bar_label(rects, padding=3)
    multiplier += 1

ax.set_ylabel("RAM (MB)")
ax.set_xlabel("Number of UAVs")
ax.set_yticks(np.arange(0, 4000 + 1, 500))
ax.set_xticks(x + width, classes)
ax.legend(loc="upper left", ncols=3)
plt.savefig(
    "/home/joao/papers/2023-joaoborges-caviarrt-ieee-journal-dblcolumn/Figures/RAM.pdf"
)
plt.close()
# ------------------------------------------------------------------------------

# plt.figure()
# plt.xlabel("CPU (%)")
# plt.ylabel("Number of occurrences")
# # plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# # plt.ylim(0, 90)
# plt.hist(
#     unreal_one_cpu,
#     bins=n_bins,
#     label="One UAV",
#     color=colors[0],
#     alpha=0.5,
# )
# plt.hist(
#     unreal_two_cpu,
#     bins=n_bins,
#     label="Two UAVs",
#     color=colors[1],
#     alpha=0.5,
# )
# plt.hist(
#     unreal_three_cpu,
#     bins=n_bins,
#     label="Three UAVs",
#     color=colors[2],
#     alpha=0.5,
# )
# plt.hist(
#     unreal_four_cpu,
#     bins=n_bins,
#     label="Four UAVs",
#     color=colors[3],
#     alpha=0.5,
# )
# plt.hist(
#     unreal_five_cpu,
#     bins=n_bins,
#     label="Five UAVs",
#     color=colors[4],
#     alpha=0.5,
# )
# plt.legend(loc="upper left")
# plt.tight_layout()
# plt.savefig("/home/joao/Downloads/caviar_records/unreal_cpu_hist.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("CPU (%)")
# plt.ylabel("Number of occurrences")
# # plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# # plt.ylim(0, 90)
# plt.hist(
#     airsim_one_cpu,
#     bins=n_bins,
#     label="One UAV",
#     color=colors[0],
#     alpha=0.5,
# )
# plt.hist(
#     airsim_two_cpu,
#     bins=n_bins,
#     label="Two UAVs",
#     color=colors[1],
#     alpha=0.5,
# )
# plt.hist(
#     airsim_three_cpu,
#     bins=n_bins,
#     label="Three UAVs",
#     color=colors[2],
#     alpha=0.5,
# )
# plt.hist(
#     airsim_four_cpu,
#     bins=n_bins,
#     label="Four UAVs",
#     color=colors[3],
#     alpha=0.5,
# )
# plt.hist(
#     airsim_five_cpu,
#     bins=n_bins,
#     label="Five UAVs",
#     color=colors[4],
#     alpha=0.5,
# )
# plt.legend(loc="upper left")
# plt.tight_layout()
# plt.savefig("/home/joao/Downloads/caviar_records/airsim_cpu_hist.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("CPU (%)")
# plt.ylabel("Number of occurrences")
# # plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# # plt.ylim(0, 90)
# plt.hist(yolo_one_cpu, bins=n_bins, label="One UAV", color=colors[0], alpha=0.5)
# plt.hist(
#     yolo_two_cpu,
#     bins=n_bins,
#     label="Two UAVs",
#     color=colors[1],
#     alpha=0.5,
# )
# plt.hist(
#     yolo_three_cpu,
#     bins=n_bins,
#     label="Three UAVs",
#     color=colors[2],
#     alpha=0.5,
# )
# plt.hist(
#     yolo_four_cpu,
#     bins=n_bins,
#     label="Four UAVs",
#     color=colors[3],
#     alpha=0.5,
# )
# plt.hist(
#     yolo_five_cpu,
#     bins=n_bins,
#     label="Five UAVs",
#     color=colors[4],
#     alpha=0.5,
# )
# plt.legend(loc="upper left")
# plt.tight_layout()
# plt.savefig("/home/joao/Downloads/caviar_records/yolo_cpu_hist.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("CPU (%)")
# plt.ylabel("Number of occurrences")
# # plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# # plt.ylim(0, 90)
# plt.hist(ns3_one_cpu, bins=n_bins, label="One UAV", color=colors[0], alpha=0.5)
# plt.hist(ns3_two_cpu, bins=n_bins, label="Two UAVs", color=colors[1], alpha=0.5)
# plt.hist(
#     ns3_three_cpu,
#     bins=n_bins,
#     label="Three UAVs",
#     color=colors[2],
#     alpha=0.5,
# )
# plt.hist(
#     ns3_four_cpu,
#     bins=n_bins,
#     label="Four UAVs",
#     color=colors[3],
#     alpha=0.5,
# )
# plt.hist(
#     ns3_five_cpu,
#     bins=n_bins,
#     label="Five UAVs",
#     color=colors[4],
#     alpha=0.5,
# )
# plt.legend(loc="upper left")
# plt.tight_layout()
# plt.savefig("/home/joao/Downloads/caviar_records/ns3_cpu_hist.pdf")
# plt.close()

# # ---------------------------------------------------------------------------

# plt.figure()
# plt.xlabel("Memory (MB)")
# plt.ylabel("Number of occurrences")
# # plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# # plt.ylim(0, 90)
# plt.hist(
#     unreal_one_ram,
#     bins=n_bins,
#     label="One UAV",
#     color=colors[0],
#     alpha=0.5,
# )
# plt.hist(
#     unreal_two_ram,
#     bins=n_bins,
#     label="Two UAVs",
#     color=colors[1],
#     alpha=0.5,
# )
# plt.hist(
#     unreal_three_ram,
#     bins=n_bins,
#     label="Three UAVs",
#     color=colors[2],
#     alpha=0.5,
# )
# plt.hist(
#     unreal_four_ram,
#     bins=n_bins,
#     label="Four UAVs",
#     color=colors[3],
#     alpha=0.5,
# )
# plt.hist(
#     unreal_five_ram,
#     bins=n_bins,
#     label="Five UAVs",
#     color=colors[4],
#     alpha=0.5,
# )
# plt.legend(loc="upper left")
# plt.tight_layout()
# plt.savefig("/home/joao/Downloads/caviar_records/unreal_ram_hist.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Memory (MB)")
# plt.ylabel("Number of occurrences")
# # plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# # plt.ylim(0, 90)
# plt.hist(
#     airsim_one_ram,
#     bins=n_bins,
#     label="One UAV",
#     color=colors[0],
#     alpha=0.5,
# )
# plt.hist(
#     airsim_two_ram,
#     bins=n_bins,
#     label="Two UAVs",
#     color=colors[1],
#     alpha=0.5,
# )
# plt.hist(
#     airsim_three_ram,
#     bins=n_bins,
#     label="Three UAVs",
#     color=colors[2],
#     alpha=0.5,
# )
# plt.hist(
#     airsim_four_ram,
#     bins=n_bins,
#     label="Four UAVs",
#     color=colors[3],
#     alpha=0.5,
# )
# plt.hist(
#     airsim_five_ram,
#     bins=n_bins,
#     label="Five UAVs",
#     color=colors[4],
#     alpha=0.5,
# )
# plt.legend(loc="upper left")
# plt.tight_layout()
# plt.savefig("/home/joao/Downloads/caviar_records/airsim_ram_hist.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Memory (MB)")
# plt.ylabel("Number of occurrences")
# # plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# # plt.ylim(0, 90)
# plt.hist(yolo_one_ram, bins=n_bins, label="One UAV", color=colors[0], alpha=0.5)
# plt.hist(
#     yolo_two_ram,
#     bins=n_bins,
#     label="Two UAVs",
#     color=colors[1],
#     alpha=0.5,
# )
# plt.hist(
#     yolo_three_ram,
#     bins=n_bins,
#     label="Three UAVs",
#     color=colors[2],
#     alpha=0.5,
# )
# plt.hist(
#     yolo_four_ram,
#     bins=n_bins,
#     label="Four UAVs",
#     color=colors[3],
#     alpha=0.5,
# )
# plt.hist(
#     yolo_five_ram,
#     bins=n_bins,
#     label="Five UAVs",
#     color=colors[4],
#     alpha=0.5,
# )
# plt.legend(loc="upper left")
# plt.tight_layout()
# plt.savefig("/home/joao/Downloads/caviar_records/yolo_ram_hist.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Memory (MB)")
# plt.ylabel("Number of occurrences")
# # plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
# # plt.ylim(0, 90)
# plt.hist(ns3_one_ram, bins=n_bins, label="One UAV", color=colors[0], alpha=0.5)
# plt.hist(ns3_two_ram, bins=n_bins, label="Two UAVs", color=colors[1], alpha=0.5)
# plt.hist(
#     ns3_three_ram,
#     bins=n_bins,
#     label="Three UAVs",
#     color=colors[2],
#     alpha=0.5,
# )
# plt.hist(
#     ns3_four_ram,
#     bins=n_bins,
#     label="Four UAVs",
#     color=colors[3],
#     alpha=0.5,
# )
# plt.hist(
#     ns3_five_ram,
#     bins=n_bins,
#     label="Five UAVs",
#     color=colors[4],
#     alpha=0.5,
# )
# plt.legend(loc="upper left")
# plt.tight_layout()
# plt.savefig("/home/joao/Downloads/caviar_records/ns3_ram_hist.pdf")
# plt.close()
