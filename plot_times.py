import numpy as np

from matplotlib import pyplot as plt
import seaborn as sns

colors = sns.color_palette("deep")
sns.set_theme()


time_ = [464.649, 591.301, 758.933, 870.339, 946.006]
real_time_factor = np.divide(time_, 60).tolist()
time_distrib = [417.508, 460.114, 700.837, 949.089, 1239.943]
# time_distrib = [417.508, 460.114, 700.837, 913, 1239.943]

time5uavs = [
    1303.842682,
    1327.299582,
    1385.423352,
    1627.740707,
    2179.130276,
    3015.853045,
    4167.647212,
    5454.171981,
]
time5uavspall = [
    1310.937925,
    1320.781043,
    1323.664657,
    1313.653765,
    1319.707581,
    1319.833231,
    1336.158407,
    1390.24421,
]
nusers = [1, 2, 3, 4, 5]

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": "Times New Roman",
        "axes.labelsize": 19,
        "xtick.labelsize": 19,
        "ytick.labelsize": 19,
        "legend.fontsize": 19,
    }
)

fig, ax1 = plt.subplots()
ax1.plot(
    nusers, time_, marker="o", color=colors[1], zorder=1
)  # Set z-order to 1 for ax1
ax1.set_xlabel("Number of connected UAVs")
ax1.set_ylabel("Total wall-clock time (seconds)", color=colors[1])
ax1.set_xlim(0.96, 5.03)
ax1.set_xticks(np.arange(1, 6, 1))
ax1.set_yticks(np.arange(400, 1000 + 1, 100))
ax1.tick_params(axis="y", colors=colors[1])

# create the second plot
ax2 = ax1.twinx()
ax2.bar(
    nusers, real_time_factor, width=0.3, color=colors[0], alpha=0.4, zorder=0
)  # Set z-order to 0 for ax2
ax2.set_ylabel("Real-time factor (RTF)", color=colors[0])
ax2.set_yticks(np.arange(0, 16 + 1, 1))
ax2.tick_params(axis="y", colors=colors[0])

plt.grid(False)
plt.tight_layout()
plt.savefig(
    "/home/joao/papers/2023-joaoborges-caviarrt-ieee-journal-dblcolumn/Figures/simulations_times.pdf"
)
