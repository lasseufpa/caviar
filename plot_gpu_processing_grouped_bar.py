import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

sns.set_theme()

colors = sns.color_palette("deep")

cwd = os.getcwd()

one_uavs_output = np.load("for_1uavs_newgpu_gpu.npz", allow_pickle=True)
two_uavs_output = np.load("for_2uavs_newgpu_gpu.npz", allow_pickle=True)
three_uavs_output = np.load("for_3uavs_newgpu_gpu.npz", allow_pickle=True)
four_uavs_output = np.load("for_4uavs_newgpu_gpu.npz", allow_pickle=True)
five_uavs_output = np.load("for_5uavs_newgpu_gpu.npz", allow_pickle=True)
ten_uavs_output = np.load("for_10uavs_newgpu_gpu.npz", allow_pickle=True)

one_uavs_central_park_cpu = one_uavs_output["central_park_cpu"]
one_uavs_python_cpu = one_uavs_output["python_cpu"]

two_uavs_central_park_cpu = two_uavs_output["central_park_cpu"]
two_uavs_python_cpu = two_uavs_output["python_cpu"]

three_uavs_central_park_cpu = three_uavs_output["central_park_cpu"]
three_uavs_python_cpu = three_uavs_output["python_cpu"]

four_uavs_central_park_cpu = four_uavs_output["central_park_cpu"]
four_uavs_python_cpu = four_uavs_output["python_cpu"]

five_uavs_central_park_cpu = five_uavs_output["central_park_cpu"]
five_uavs_python_cpu = five_uavs_output["python_cpu"]

ten_uavs_central_park_cpu = ten_uavs_output["central_park_cpu"]
ten_uavs_python_cpu = ten_uavs_output["python_cpu"]

# classes = ["One", "Two", "Three", "Four", "Five", "Ten"]
classes = ["One", "Three", "Five", "Ten"]

gpu_proc_means = {
    "Mob+3D": (
        np.mean(one_uavs_central_park_cpu),
        # np.mean(two_uavs_central_park_cpu),
        np.mean(three_uavs_central_park_cpu),
        # np.mean(four_uavs_central_park_cpu),
        np.mean(five_uavs_central_park_cpu),
        np.mean(ten_uavs_central_park_cpu),
    ),
    "Communications": (
        np.mean(one_uavs_python_cpu),
        # np.mean(two_uavs_python_cpu),
        np.mean(three_uavs_python_cpu),
        # np.mean(four_uavs_python_cpu),
        np.mean(five_uavs_python_cpu),
        np.mean(ten_uavs_python_cpu),
    ),
    "Total": (
        np.mean(one_uavs_python_cpu) + np.mean(one_uavs_central_park_cpu),
        # np.mean(two_uavs_python_cpu) + np.mean(two_uavs_central_park_cpu),
        np.mean(three_uavs_python_cpu) + np.mean(three_uavs_central_park_cpu),
        # np.mean(four_uavs_python_cpu) + np.mean(four_uavs_central_park_cpu),
        np.mean(five_uavs_python_cpu) + np.mean(five_uavs_central_park_cpu),
        np.mean(ten_uavs_python_cpu) + np.mean(ten_uavs_central_park_cpu),
    ),
}

hatches = {
    "Mob+3D": "",
    "Communications": "/",
    "Total": "|",
}

curr_colors = {
    "Mob+3D": colors[1],
    "Communications": colors[0],
    "Total": colors[4],
}

x = np.arange(len(classes))
width = 0.17
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

for idx, ((attribute, measurement), curr_hatch, curr_color) in enumerate(
    zip(gpu_proc_means.items(), hatches.values(), curr_colors.values())
):
    offset = width * multiplier

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

ax.set_yticks(np.arange(0, 100 + 1, 10))
ax.set_xticks(x + width, classes)
ax.legend(loc="upper left", ncols=3)
ax.set_ylim(0, 100)
ax.set_xlabel("Number of UAVs")
ax.set_ylabel("Usage (%)")
plt.savefig(
    "/home/joao/papers/2023-joaoborges-caviarrt-ieee-journal-dblcolumn/Figures/gpu_cpu.pdf"
)
