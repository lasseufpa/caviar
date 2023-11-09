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

# ------------------------------------------------------------------------------

x = ["One", "Two", "Three", "Four", "Five"]
sionna_gpu_proc = [
    np.mean(one_uavs_python_cpu),
    np.mean(two_uavs_python_cpu),
    np.mean(three_uavs_python_cpu),
    np.mean(four_uavs_python_cpu),
    np.mean(five_uavs_python_cpu),
]
unreal_gpu_proc = [
    np.mean(one_uavs_central_park_cpu),
    np.mean(two_uavs_central_park_cpu),
    np.mean(three_uavs_central_park_cpu),
    np.mean(four_uavs_central_park_cpu),
    np.mean(five_uavs_central_park_cpu),
]

# ------------------------------------------------------------------------------
plt.figure(figsize=(26, 6))
plt.bar(x, sionna_gpu_proc, hatch="/", label="Communications", color=colors[3])
plt.bar(
    x, unreal_gpu_proc, hatch="", bottom=sionna_gpu_proc, label="3D", color=colors[0]
)
plt.legend()
plt.yticks(np.arange(0, 100 + 1, 5))
plt.ylim(0, 100, 5)
plt.xlabel("Number of UAVs")
plt.ylabel("Usage (%)")
plt.savefig(
    "/home/joao/papers/2023-joaoborges-caviarrt-ieee-journal-dblcolumn/Figures/gpu_cpu.pdf"
)
