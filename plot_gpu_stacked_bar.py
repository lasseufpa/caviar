import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# For 1 UAV
# Communications 64%
# 3D             12%
# Total          76%

# For 2 UAV
# Communications 61%
# 3D             14%
# Total          75%

# For 3 UAV
# Communications 59%
# 3D             16%
# Total          75%

# For 4 UAV
# Communications 57%
# 3D             18%
# Total          75%

# For 5 UAV
# Communications 55%
# 3D             20%
# Total          75%

# For 10 UAV:
# Communications 45%
# 3D             29%
# Total          74%
sns.set_theme()
colors = sns.color_palette("deep")

classes = ["One", "Three", "Five", "Ten"]

ram_means = {
    "Mob+3D": (
        12,
        16,
        20,
        29,
    ),
    "Communications": (64, 59, 55, 45),
    "Total": (
        76,
        75,
        75,
        74,
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
width = 0.20
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
    zip(ram_means.items(), hatches.values(), curr_colors.values())
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

ax.set_ylabel("CPU (%)")
ax.set_yticks(np.arange(0, 100 + 1, 10))
ax.set_xticks(x + width, classes)
ax.legend(loc="upper left", ncols=3)
ax.set_ylim(0, 100)
ax.set_xlabel("Number of UAVs")
ax.set_ylabel("Usage (%)")
plt.savefig(
    "/home/joao/papers/2023-joaoborges-caviarrt-ieee-journal-dblcolumn/Figures/gpu_ram.pdf"
)
# plt.savefig("/home/joao/Downloads/caviar_records/CPU.pdf")
# plt.close()


# ------------------------------------------------------------------------------
# plt.figure(figsize=(26, 6))
# plt.bar(x, sionna_gpu_mem, hatch="/", label="Communications", color=colors[3])
# plt.bar(x, unreal_gpu_mem, hatch="", bottom=sionna_gpu_mem, label="3D", color=colors[0])
# plt.legend()
# plt.yticks(np.arange(0, 100 + 1, 5))
