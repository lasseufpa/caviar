import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

sns.set_theme()

colors = sns.color_palette("deep")

mv_avg = 50


def moving_average(x, w):
    return np.convolve(x, np.ones(w), "valid") / w


cwd = os.getcwd()

one_uavs_output = np.load("for_1uavs_newgpu_gpu.npz", allow_pickle=True)
two_uavs_output = np.load("for_2uavs_newgpu_gpu.npz", allow_pickle=True)
five_uavs_output = np.load("for_5uavs_newgpu_gpu.npz", allow_pickle=True)

# (rows)       (columns)       (patterns)
#  cpu      1uav 2uav 5uav      3D/comm
#  ram      1uav 2uav 5uav      3D/comm

one_uavs_central_park_cpu = moving_average(one_uavs_output["central_park_cpu"], mv_avg)
one_uavs_python_cpu = moving_average(one_uavs_output["python_cpu"], mv_avg)

two_uavs_central_park_cpu = moving_average(two_uavs_output["central_park_cpu"], mv_avg)
two_uavs_python_cpu = moving_average(two_uavs_output["python_cpu"], mv_avg)

five_uavs_central_park_cpu = moving_average(
    five_uavs_output["central_park_cpu"], mv_avg
)
five_uavs_python_cpu = moving_average(five_uavs_output["python_cpu"], mv_avg)


one_uavs_central_park_ram = moving_average(one_uavs_output["central_park_ram"], mv_avg)
one_uavs_python_ram = moving_average(one_uavs_output["python_ram"], mv_avg)

two_uavs_central_park_ram = moving_average(two_uavs_output["central_park_ram"], mv_avg)
two_uavs_python_ram = moving_average(two_uavs_output["python_ram"], mv_avg)

five_uavs_central_park_ram = moving_average(
    five_uavs_output["central_park_ram"], mv_avg
)
five_uavs_python_ram = moving_average(five_uavs_output["python_ram"], mv_avg)

print(len(one_uavs_output["central_park_cpu"]))
print(len(two_uavs_output["central_park_cpu"]))
print(len(five_uavs_output["central_park_cpu"]))
# ------------------------------------------------------------------------------
plt.figure()

filling = len(one_uavs_python_cpu) - len(one_uavs_central_park_cpu)
adjusted_array = np.append(one_uavs_central_park_cpu, np.zeros(filling))
total = one_uavs_python_cpu + adjusted_array

plt.plot(range(len(total)), total, label="Total", linestyle="solid", color=colors[5])
plt.plot(
    range(len(one_uavs_central_park_cpu)),
    one_uavs_central_park_cpu,
    label="3D",
    linestyle="dotted",
    color=colors[0],
)
plt.plot(
    range(len(one_uavs_python_cpu)),
    one_uavs_python_cpu,
    label="Comm.",
    linestyle="dashed",
    color=colors[3],
)

plt.grid(True)
plt.legend()
plt.ylim(0, 60, 10)
plt.xlabel("Time step (n)")
plt.ylabel("Usage (%)")
plt.savefig(
    "./output/gpu_one_uavs_cpu.pdf"
)

# ------------------------------------------------------------------------------
plt.figure()

filling = len(two_uavs_python_cpu) - len(two_uavs_central_park_cpu)
adjusted_array = np.append(two_uavs_central_park_cpu, np.zeros(filling))
total = two_uavs_python_cpu + adjusted_array

plt.plot(range(len(total)), total, label="Total", linestyle="solid", color=colors[5])
plt.plot(
    range(len(two_uavs_central_park_cpu)),
    two_uavs_central_park_cpu,
    label="3D",
    linestyle="dotted",
    color=colors[0],
)
plt.plot(
    range(len(two_uavs_python_cpu)),
    two_uavs_python_cpu,
    label="Comm.",
    linestyle="dashed",
    color=colors[3],
)
plt.grid(True)
plt.legend()
plt.ylim(0, 60, 10)
plt.xlabel("Time step (n)")
plt.ylabel("Usage (%)")
plt.savefig(
    "./output/gpu_two_uavs_cpu.pdf"
)

# ------------------------------------------------------------------------------
plt.figure()

filling = len(five_uavs_python_cpu) - len(five_uavs_central_park_cpu)
adjusted_array = np.append(five_uavs_central_park_cpu, np.zeros(filling))
total = five_uavs_python_cpu + adjusted_array

plt.plot(range(len(total)), total, label="Total", linestyle="solid", color=colors[5])
plt.plot(
    range(len(five_uavs_central_park_cpu)),
    five_uavs_central_park_cpu,
    label="3D",
    linestyle="dotted",
    color=colors[0],
)
plt.plot(
    range(len(five_uavs_python_cpu)),
    five_uavs_python_cpu,
    label="Comm.",
    linestyle="dashed",
    color=colors[3],
)
plt.grid(True)
plt.legend()
plt.ylim(0, 60, 10)
plt.xlabel("Time step (n)")
plt.ylabel("Usage (%)")
plt.savefig(
    "./output/gpu_five_uavs_cpu.pdf"
)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
plt.figure()
plt.plot(
    range(len(one_uavs_central_park_ram)),
    one_uavs_central_park_ram,
    label="3D",
    linestyle="solid",
)
plt.plot(
    range(len(one_uavs_python_ram)),
    one_uavs_python_ram,
    label="Comm.",
    linestyle="dashed",
)
plt.grid(True)
plt.legend()
plt.ylim(0, 8)
plt.xlabel("Time step (n)")
plt.ylabel("Usage (%)")
plt.savefig(
    "./output/gpu_one_uavs_ram.pdf"
)

# ------------------------------------------------------------------------------
plt.figure()
plt.plot(
    range(len(two_uavs_central_park_ram)),
    two_uavs_central_park_ram,
    label="3D",
    linestyle="solid",
)
plt.plot(
    range(len(two_uavs_python_ram)),
    two_uavs_python_ram,
    label="Comm.",
    linestyle="dashed",
)
plt.grid(True)
plt.legend()
plt.ylim(0, 8)
plt.xlabel("Time step (n)")
plt.ylabel("Usage (%)")
plt.savefig(
    "./output/gpu_two_uavs_ram.pdf"
)

# ------------------------------------------------------------------------------
plt.figure()
plt.plot(
    range(len(five_uavs_central_park_ram)),
    five_uavs_central_park_ram,
    label="3D",
    linestyle="solid",
)
plt.plot(
    range(len(five_uavs_python_ram)),
    five_uavs_python_ram,
    label="Comm.",
    linestyle="dashed",
)
plt.grid(True)
plt.legend()
plt.ylim(0, 8)
plt.xlabel("Time step (n)")
plt.ylabel("Usage (%)")
plt.savefig(
    "./output/gpu_five_uavs_ram.pdf"
)

# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# plt.figure()
# plt.hist(one_uavs_central_park_cpu, label="3D", bins=10)
# plt.hist(one_uavs_python_cpu, label="Comm.", bins=10, alpha=0.5)
# plt.grid(True)
# plt.legend()
# # plt.yticks(np.arange(-90, 21, 10))
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("./output/gpu_hist_one_uavs_cpu.pdf")

# # ------------------------------------------------------------------------------
# plt.figure()
# plt.hist(two_uavs_central_park_cpu, label="3D", bins=10)
# plt.hist(two_uavs_python_cpu, label="Comm.", bins=10, alpha=0.5)
# plt.grid(True)
# plt.legend()
# # plt.yticks(np.arange(-90, 21, 10))
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("./output/gpu_hist_two_uavs_cpu.pdf")

# # ------------------------------------------------------------------------------
# plt.figure()
# plt.hist(five_uavs_central_park_cpu, label="3D", bins=10)
# plt.hist(five_uavs_python_cpu, label="Comm.", bins=10, alpha=0.5)
# plt.grid(True)
# plt.legend()
# # plt.yticks(np.arange(-90, 21, 10))
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("./output/gpu_hist_five_uavs_cpu.pdf")

# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# plt.figure()
# plt.hist(one_uavs_central_park_ram, label="3D", bins=10)
# plt.hist(one_uavs_python_ram, label="Comm.", bins=10, alpha=0.5)
# plt.grid(True)
# plt.legend()
# # plt.yticks(np.arange(-90, 21, 10))
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("./output/gpu_hist_one_uavs_ram.pdf")

# # ------------------------------------------------------------------------------
# plt.figure()
# plt.hist(two_uavs_central_park_ram, label="3D", bins=10)
# plt.hist(two_uavs_python_ram, label="Comm.", bins=10, alpha=0.5)
# plt.grid(True)
# plt.legend()
# # plt.yticks(np.arange(-90, 21, 10))
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("./output/gpu_hist_two_uavs_ram.pdf")

# # ------------------------------------------------------------------------------
# plt.figure()
# plt.hist(five_uavs_central_park_ram, label="3D", bins=10)
# plt.hist(five_uavs_python_ram, label="Comm.", bins=10, alpha=0.5)
# plt.grid(True)
# plt.legend()
# # plt.yticks(np.arange(-90, 21, 10))
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("./output/gpu_hist_five_uavs_ram.pdf")
