# https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html
# data from https://allisonhorst.github.io/palmerpenguins/

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

colors = sns.color_palette("deep")

sns.set_theme()

groups = ("One", "Two", "Three", "Four", "Five")
means = {
    "3D": (18.35, 18.43, 14.98, 15.50, 16.5),
    "AI": (38.79, 48.83, 47.50, 50.1, 55.3),
    "Orchestrator": (20, 21, 22, 23, 24),
    "Communications": (189.95, 195.82, 217.19, 220.4, 225.1),
    "Total": (220, 230, 240, 250, 260),
}

std_devs = {
    "3D": (18.35, 18.43, 14.98, 15.50, 16.5),
    "AI": (38.79, 48.83, 47.50, 50.1, 55.3),
    "Orchestrator": (20, 21, 22, 23, 24),
    "Communications": (189.95, 195.82, 217.19, 220.4, 225.1),
    "Total": (220, 230, 240, 250, 260),
}

hatches = {
    "3D": "",
    "AI": "1",
    "Orchestrator": ".",
    "Communications": "/",
    "Total": "*",
}

plots_configs = [means, std_devs, hatches]

x = np.arange(len(groups))  # the label locations
width = 0.18  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout="constrained")

for idx, ((attribute, measurement), std_dev, curr_hatch) in enumerate(
    zip(means.items(), std_devs.values(), hatches.values())
):
    offset = width * multiplier

    if attribute == "Total":
        curr_color = colors[5]
    else:
        curr_color = colors[idx]

    rects = ax.bar(
        x + offset,
        measurement,
        width,
        yerr=std_dev,
        hatch=curr_hatch,
        color=curr_color,
        label=attribute,
    )

    ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel("CPU (%)")
ax.set_xticks(x + width, groups)
ax.legend(loc="upper left", ncols=3)

plt.show()
