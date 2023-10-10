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


time_ = [464.649, 591.301, 758.933, 870.339, 946.006]
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

# plt.figure(figsize=(5.4,3.6))
plt.xlabel("Nº of users")
plt.ylabel("Elapsed time (seconds)")
plt.xlim(0.95, 5.05)
plt.xticks(np.arange(1, 6, 1))
# plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
plt.plot(nusers, time_, marker="o", color=colors[1])
# plt.plot(
#     nusers, time_, marker="o", color=colors[1], label="Monolithic execution (1 PC)"
# )
# plt.plot(
#     nusers,
#     time_distrib,
#     marker="*",
#     color=colors[2],
#     label="Distributed execution (2 PCs)",
# )
# plt.plot(nusers,time5uavs, marker='', label='Simulation considering five UAVs', color=colors[2])
# plt.plot(nusers,time5uavspall, marker='', label='Simulation considering five UAVs using parallel computing', color=colors[3])


# plt.legend()
# plt.legend(loc='upper left')
# plt.grid()

plt.tight_layout()
# plt.savefig('../figures/graphs/results_time/simulations_times.pgf')
plt.savefig(
    "/home/joao/papers/2023-joaoborges-caviarrt-ieee-journal-dblcolumn/Figures/simulations_times.pdf"
)
