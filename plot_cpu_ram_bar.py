import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

colors = sns.color_palette("deep")

sns.set_theme()

simode = "newgpu"
n_bins = 50


one_uav_3D_data_filepath = (
    "/output/caviar_records/for_1uavs_newgpu_airsim.txt"
)
one_uav_AI_data_filepath = (
    "./output/caviar_records/for_1uavs_newgpu_mobility.txt"
)
one_uav_comm_data_filepath = (
    "./output/caviar_records/for_1uavs_newgpu_sionna.txt"
)
one_uav_orchestrator_data_filepath = (
    "./output/caviar_records/for_1uavs_newgpu_nats.txt"
)

two_uav_3D_data_filepath = (
    "./output/caviar_records/for_2uavs_newgpu_airsim.txt"
)
two_uav_AI_data_filepath = (
    "./output/caviar_records/for_2uavs_newgpu_mobility.txt"
)
two_uav_comm_data_filepath = (
    "./output/caviar_records/for_2uavs_newgpu_sionna.txt"
)
two_uav_orchestrator_data_filepath = (
    "./output/caviar_records/for_2uavs_newgpu_nats.txt"
)

three_uav_3D_data_filepath = (
    "./output/caviar_records/for_3uavs_newgpu_airsim.txt"
)
three_uav_AI_data_filepath = (
    "./output/caviar_records/for_3uavs_newgpu_mobility.txt"
)
three_uav_comm_data_filepath = (
    "./output/caviar_records/for_3uavs_newgpu_sionna.txt"
)
three_uav_orchestrator_data_filepath = (
    "./output/caviar_records/for_3uavs_newgpu_nats.txt"
)

four_uav_3D_data_filepath = (
    "./output/caviar_records/for_4uavs_newgpu_airsim.txt"
)
four_uav_AI_data_filepath = (
    "./output/caviar_records/for_4uavs_newgpu_mobility.txt"
)
four_uav_comm_data_filepath = (
    "./output/caviar_records/for_4uavs_newgpu_sionna.txt"
)
four_uav_orchestrator_data_filepath = (
    "./output/caviar_records/for_4uavs_newgpu_nats.txt"
)

five_uav_3D_data_filepath = (
    "./output/caviar_records/for_5uavs_newgpu_airsim.txt"
)
five_uav_AI_data_filepath = (
    "./output/caviar_records/for_5uavs_newgpu_mobility.txt"
)
five_uav_comm_data_filepath = (
    "./output/caviar_records/for_5uavs_newgpu_sionna.txt"
)
five_uav_orchestrator_data_filepath = (
    "./output/caviar_records/for_5uavs_newgpu_nats.txt"
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


threeD_one = np.array(readFromFile(one_uav_3D_data_filepath), dtype=float)
threeD_two = np.array(readFromFile(two_uav_3D_data_filepath), dtype=float)
threeD_three = np.array(readFromFile(three_uav_3D_data_filepath), dtype=float)
threeD_four = np.array(readFromFile(four_uav_3D_data_filepath), dtype=float)
threeD_five = np.array(readFromFile(five_uav_3D_data_filepath), dtype=float)

AI_one = np.array(readFromFile(one_uav_AI_data_filepath), dtype=float)
AI_two = np.array(readFromFile(two_uav_AI_data_filepath), dtype=float)
AI_three = np.array(readFromFile(three_uav_AI_data_filepath), dtype=float)
AI_four = np.array(readFromFile(four_uav_AI_data_filepath), dtype=float)
AI_five = np.array(readFromFile(five_uav_AI_data_filepath), dtype=float)

comm_one = np.array(readFromFile(one_uav_comm_data_filepath), dtype=float)
comm_two = np.array(readFromFile(two_uav_comm_data_filepath), dtype=float)
comm_three = np.array(readFromFile(three_uav_comm_data_filepath), dtype=float)
comm_four = np.array(readFromFile(four_uav_comm_data_filepath), dtype=float)
comm_five = np.array(readFromFile(five_uav_comm_data_filepath), dtype=float)

orchestrator_one = np.array(
    readFromFile(one_uav_orchestrator_data_filepath), dtype=float
)
orchestrator_two = np.array(
    readFromFile(two_uav_orchestrator_data_filepath), dtype=float
)
orchestrator_three = np.array(
    readFromFile(three_uav_orchestrator_data_filepath), dtype=float
)
orchestrator_four = np.array(
    readFromFile(four_uav_orchestrator_data_filepath), dtype=float
)
orchestrator_five = np.array(
    readFromFile(five_uav_orchestrator_data_filepath), dtype=float
)

threeD_one_cpu = threeD_one[:, 1] / 12
threeD_two_cpu = threeD_two[:, 1] / 12
threeD_three_cpu = threeD_three[:, 1] / 12
threeD_four_cpu = threeD_four[:, 1] / 12
threeD_five_cpu = threeD_five[:, 1] / 12
threeD_one_ram = threeD_one[:, 2]
threeD_two_ram = threeD_two[:, 2]
threeD_three_ram = threeD_three[:, 2]
threeD_four_ram = threeD_four[:, 2]
threeD_five_ram = threeD_five[:, 2]

AI_one_cpu = AI_one[:, 1] / 12
AI_two_cpu = AI_two[:, 1] / 12
AI_three_cpu = AI_three[:, 1] / 12
AI_four_cpu = AI_four[:, 1] / 12
AI_five_cpu = AI_five[:, 1] / 12
AI_one_ram = AI_one[:, 2]
AI_two_ram = AI_two[:, 2]
AI_three_ram = AI_three[:, 2]
AI_four_ram = AI_four[:, 2]
AI_five_ram = AI_five[:, 2]

comm_one_cpu = comm_one[:, 1] / 12
comm_two_cpu = comm_two[:, 1] / 12
comm_three_cpu = comm_three[:, 1] / 12
comm_four_cpu = comm_four[:, 1] / 12
comm_five_cpu = comm_five[:, 1] / 12
comm_one_ram = comm_one[:, 2]
comm_two_ram = comm_two[:, 2]
comm_three_ram = comm_three[:, 2]
comm_four_ram = comm_four[:, 2]
comm_five_ram = comm_five[:, 2]

orchestrator_one_cpu = orchestrator_one[:, 1] / 12
orchestrator_two_cpu = orchestrator_two[:, 1] / 12
orchestrator_three_cpu = orchestrator_three[:, 1] / 12
orchestrator_four_cpu = orchestrator_four[:, 1] / 12
orchestrator_five_cpu = orchestrator_five[:, 1] / 12
orchestrator_one_ram = orchestrator_one[:, 2]
orchestrator_two_ram = orchestrator_two[:, 2]
orchestrator_three_ram = orchestrator_three[:, 2]
orchestrator_four_ram = orchestrator_four[:, 2]
orchestrator_five_ram = orchestrator_five[:, 2]

one_cpu = threeD_one_cpu + AI_one_cpu + comm_one_cpu + orchestrator_one_cpu
two_cpu = threeD_two_cpu + AI_two_cpu + comm_two_cpu + orchestrator_two_cpu
three_cpu = threeD_three_cpu + AI_three_cpu + comm_three_cpu + orchestrator_three_cpu
four_cpu = threeD_four_cpu + AI_four_cpu + comm_four_cpu + orchestrator_four_cpu
five_cpu = threeD_five_cpu + AI_five_cpu + comm_five_cpu + orchestrator_five_cpu
one_ram = threeD_one_ram + AI_one_ram + comm_one_ram + orchestrator_one_ram
two_ram = threeD_two_ram + AI_two_ram + comm_two_ram + orchestrator_two_ram
three_ram = threeD_three_ram + AI_three_ram + comm_three_ram + orchestrator_three_ram
four_ram = threeD_four_ram + AI_four_ram + comm_four_ram + orchestrator_four_ram
five_ram = threeD_five_ram + AI_five_ram + comm_five_ram + orchestrator_five_ram

plt.figure()
plt.xlabel("Number of UAVs")
plt.ylabel("CPU (%)")
# plt.ylim(0, 90)
plt.bar(
    ["One", "Two", "Three", "Four", "Five"],
    [
        np.mean(threeD_one_cpu),
        np.mean(threeD_two_cpu),
        np.mean(threeD_three_cpu),
        np.mean(threeD_four_cpu),
        np.mean(threeD_five_cpu),
    ],
    yerr=[
        np.std(threeD_one_cpu),
        np.std(threeD_two_cpu),
        np.std(threeD_three_cpu),
        np.std(threeD_four_cpu),
        np.std(threeD_five_cpu),
    ],
    color=colors,
    alpha=0.5,
)
# plt.tight_layout()
# plt.savefig("./output/caviar_records/threeD_cpu_bar.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Number of UAVs")
# plt.ylabel("CPU (%)")
# plt.ylim(0, 90)
plt.bar(
    ["One", "Two", "Three", "Four", "Five"],
    [
        np.mean(AI_one_cpu),
        np.mean(AI_two_cpu),
        np.mean(AI_three_cpu),
        np.mean(AI_four_cpu),
        np.mean(AI_five_cpu),
    ],
    yerr=[
        np.std(AI_one_cpu),
        np.std(AI_two_cpu),
        np.std(AI_three_cpu),
        np.std(AI_four_cpu),
        np.std(AI_five_cpu),
    ],
    color=colors,
    alpha=0.5,
)
# plt.tight_layout()
# plt.savefig("./output/caviar_records/AI_cpu_bar.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Number of UAVs")
# plt.ylabel("CPU (%)")
# plt.ylim(0, 90)
plt.bar(
    ["One", "Two", "Three", "Four", "Five"],
    [
        np.mean(comm_one_cpu),
        np.mean(comm_two_cpu),
        np.mean(comm_three_cpu),
        np.mean(comm_four_cpu),
        np.mean(comm_five_cpu),
    ],
    yerr=[
        np.std(comm_one_cpu),
        np.std(comm_two_cpu),
        np.std(comm_three_cpu),
        np.std(comm_four_cpu),
        np.std(comm_five_cpu),
    ],
    color=colors,
    alpha=0.5,
)
# plt.tight_layout()
# plt.savefig("./output/caviar_records/comm_cpu_bar.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Number of UAVs")
# plt.ylabel("CPU (%)")
# plt.ylim(0, 90)
plt.bar(
    ["One", "Two", "Three", "Four", "Five"],
    [
        np.mean(orchestrator_one_cpu),
        np.mean(orchestrator_two_cpu),
        np.mean(orchestrator_three_cpu),
        np.mean(orchestrator_four_cpu),
        np.mean(orchestrator_five_cpu),
    ],
    yerr=[
        np.std(orchestrator_one_cpu),
        np.std(orchestrator_two_cpu),
        np.std(orchestrator_three_cpu),
        np.std(orchestrator_four_cpu),
        np.std(orchestrator_five_cpu),
    ],
    color=colors,
    alpha=0.5,
)
plt.tight_layout()
# plt.savefig("./output/caviar_records/orchestrator_cpu_bar.pdf")
plt.savefig("./output/caviar_records/cpu_bar.pdf")
plt.close()

# # ---------------------------------------------------------------------------

# plt.figure()
# plt.xlabel("Number of UAVs")
# plt.ylabel("Memory (MB)")
# plt.ylim(0, 90)
plt.bar(
    ["One", "Two", "Three", "Four", "Five"],
    [
        np.mean(threeD_one_ram),
        np.mean(threeD_two_ram),
        np.mean(threeD_three_ram),
        np.mean(threeD_four_ram),
        np.mean(threeD_five_ram),
    ],
    yerr=[
        np.std(threeD_one_ram),
        np.std(threeD_two_ram),
        np.std(threeD_three_ram),
        np.std(threeD_four_ram),
        np.std(threeD_five_ram),
    ],
    color=colors,
    alpha=0.5,
)
# plt.tight_layout()
# plt.savefig("./output/caviar_records/threeD_ram_bar.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Number of UAVs")
# plt.ylabel("Memory (MB)")
# plt.ylim(0, 90)
plt.bar(
    ["One", "Two", "Three", "Four", "Five"],
    [
        np.mean(AI_one_ram),
        np.mean(AI_two_ram),
        np.mean(AI_three_ram),
        np.mean(AI_four_ram),
        np.mean(AI_five_ram),
    ],
    yerr=[
        np.std(AI_one_ram),
        np.std(AI_two_ram),
        np.std(AI_three_ram),
        np.std(AI_four_ram),
        np.std(AI_five_ram),
    ],
    color=colors,
    alpha=0.5,
)
# plt.tight_layout()
# plt.savefig("./output/caviar_records/AI_ram_bar.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Number of UAVs")
# plt.ylabel("Memory (MB)")
# plt.ylim(0, 90)
plt.bar(
    ["One", "Two", "Three", "Four", "Five"],
    [
        np.mean(comm_one_ram),
        np.mean(comm_two_ram),
        np.mean(comm_three_ram),
        np.mean(comm_four_ram),
        np.mean(comm_five_ram),
    ],
    yerr=[
        np.std(comm_one_ram),
        np.std(comm_two_ram),
        np.std(comm_three_ram),
        np.std(comm_four_ram),
        np.std(comm_five_ram),
    ],
    color=colors,
    alpha=0.5,
)
# plt.tight_layout()
# plt.savefig("./output/caviar_records/comm_ram_bar.pdf")
# plt.close()

# plt.figure()
# plt.xlabel("Number of UAVs")
# plt.ylabel("Memory (MB)")
# plt.ylim(0, 90)
plt.bar(
    ["One", "Two", "Three", "Four", "Five"],
    [
        np.mean(orchestrator_one_ram),
        np.mean(orchestrator_two_ram),
        np.mean(orchestrator_three_ram),
        np.mean(orchestrator_four_ram),
        np.mean(orchestrator_five_ram),
    ],
    yerr=[
        np.std(orchestrator_one_ram),
        np.std(orchestrator_two_ram),
        np.std(orchestrator_three_ram),
        np.std(orchestrator_four_ram),
        np.std(orchestrator_five_ram),
    ],
    color=colors,
    alpha=0.5,
)
plt.tight_layout()
# plt.savefig("./output/caviar_records/orchestrator_ram_bar.pdf")
plt.savefig("./output/caviar_records/ram_bar.pdf")
plt.close()
