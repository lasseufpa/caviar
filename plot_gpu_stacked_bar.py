import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# For 1 UVA

# Sionna 64%
# Unreal 12%

# For 2 UVA

# Sionna 61%
# Unreal 14%

# For 3 UVA

# Sionna 59%
# Unreal 16%

# For 4 UVA

# Sionna 57%
# Unreal 18%

# For 5 UVA

# Sionna 55%
# Unreal 20%

sns.set_theme()
colors = sns.color_palette("deep")

classes = ["One", "Two", "Three", "Four", "Five"]

ram_means = {
    "3D": (
        12,
        14,
        16,
        18,
        20,
    ),
    "Communications": (64, 61, 59, 57, 55),
    "Total": (
        76,
        75,
        75,
        75,
        75,
    ),
}

hatches = {
    "3D": "",
    "Communications": "/",
    "Total": "|",
}

curr_colors = {
    "3D": colors[0],
    "Communications": colors[3],
    "Total": colors[4],
}

x = np.arange(len(classes))
width = 0.17
multiplier = 0

fig, ax = plt.subplots(layout="constrained")
fig.set_figwidth(25)
fig.set_figheight(7)

for idx, ((attribute, measurement), curr_hatch, curr_color) in enumerate(
    zip(ram_means.items(), hatches.values(), curr_colors.values())
):
    offset = width * multiplier

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
