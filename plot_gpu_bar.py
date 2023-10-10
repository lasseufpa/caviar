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

x = ["One", "Two", "Three", "Four", "Five"]
sionna_gpu_mem = [64, 61, 59, 57, 55]
unreal_gpu_mem = [12, 14, 16, 18, 20]

# x = ["One", "Two", "Five"]
# sionna_gpu_mem = [64, 61, 55]
# unreal_gpu_mem = [12, 14, 20]


# ------------------------------------------------------------------------------
plt.figure(figsize=(26, 6))
plt.bar(x, sionna_gpu_mem, hatch="/", label="Communications", color=colors[3])
plt.bar(x, unreal_gpu_mem, hatch="", bottom=sionna_gpu_mem, label="3D", color=colors[0])
plt.legend()
plt.yticks(np.arange(0, 100 + 1, 5))
plt.ylim(0, 100, 5)
plt.xlabel("Number of UAVs")
plt.ylabel("Usage (%)")
plt.savefig(
    "/home/joao/papers/2023-joaoborges-caviarrt-ieee-journal-dblcolumn/Figures/gpu_ram.pdf"
)
# # ------------------------------------------------------------------------------
# plt.figure()
# plt.plot(
#     range(len(two_uavs_central_park_cpu)),
#     two_uavs_central_park_cpu,
#     label="3D",
#     linestyle="solid",
# )
# plt.plot(
#     range(len(two_uavs_python_cpu)),
#     two_uavs_python_cpu,
#     label="Comm.",
#     linestyle="dashed",
# )
# plt.grid(True)
# plt.legend()
# plt.ylim(0, 60, 10)
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("gpu_two_uavs_cpu.pdf")

# # ------------------------------------------------------------------------------
# plt.figure()
# plt.plot(
#     range(len(five_uavs_central_park_cpu)),
#     five_uavs_central_park_cpu,
#     label="3D",
#     linestyle="solid",
# )
# plt.plot(
#     range(len(five_uavs_python_cpu)),
#     five_uavs_python_cpu,
#     label="Comm.",
#     linestyle="dashed",
# )
# plt.grid(True)
# plt.legend()
# plt.ylim(0, 60, 10)
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("gpu_five_uavs_cpu.pdf")

# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# # ------------------------------------------------------------------------------
# plt.figure()
# plt.plot(
#     range(len(one_uavs_central_park_ram)),
#     one_uavs_central_park_ram,
#     label="3D",
#     linestyle="solid",
# )
# plt.plot(
#     range(len(one_uavs_python_ram)),
#     one_uavs_python_ram,
#     label="Comm.",
#     linestyle="dashed",
# )
# plt.grid(True)
# plt.legend()
# plt.ylim(0, 8)
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("gpu_one_uavs_ram.pdf")

# # ------------------------------------------------------------------------------
# plt.figure()
# plt.plot(
#     range(len(two_uavs_central_park_ram)),
#     two_uavs_central_park_ram,
#     label="3D",
#     linestyle="solid",
# )
# plt.plot(
#     range(len(two_uavs_python_ram)),
#     two_uavs_python_ram,
#     label="Comm.",
#     linestyle="dashed",
# )
# plt.grid(True)
# plt.legend()
# plt.ylim(0, 8)
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("gpu_two_uavs_ram.pdf")

# # ------------------------------------------------------------------------------
# plt.figure()
# plt.plot(
#     range(len(five_uavs_central_park_ram)),
#     five_uavs_central_park_ram,
#     label="3D",
#     linestyle="solid",
# )
# plt.plot(
#     range(len(five_uavs_python_ram)),
#     five_uavs_python_ram,
#     label="Comm.",
#     linestyle="dashed",
# )
# plt.grid(True)
# plt.legend()
# plt.ylim(0, 8)
# plt.xlabel("Time step (n)")
# plt.ylabel("Usage (%)")
# plt.savefig("gpu_five_uavs_ram.pdf")
