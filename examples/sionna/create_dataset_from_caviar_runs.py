import numpy as np
import os
from os import listdir

current_dir = os.getcwd()
dataset_dir = os.path.join(current_dir, "runs")
# dataset_dir = os.path.join(
#     current_dir, "data_study", "LOS_and_NLOS_caviar_run03", "LOS"
# )
# dataset_dir = os.path.join(
#     current_dir, "data_study", "LOS_and_NLOS_caviar_run03", "NLOS"
# )

rx_airsim_position = []
rx_starting_position = []
rx_current_position = []
mimoChannel = []
equivalentChannel = []
equivalentChannelMagnitude = []
best_ray = []
bit_rate = []

onlynpz = [file for file in listdir(dataset_dir) if file[-3:] == "npz"]
for i in range(len(onlynpz)):
    dataset_file_name = str(onlynpz[i])
    dataset_file = os.path.join(dataset_dir, dataset_file_name)
    caviar_output = np.load(dataset_file, allow_pickle=True)
    rx_airsim_position.append(caviar_output["rx_airsim_position"])
    rx_starting_position.append(caviar_output["rx_starting_position"])
    rx_current_position.append(caviar_output["rx_current_position"])
    mimoChannel.append(caviar_output["mimoChannel"])
    equivalentChannel.append(caviar_output["equivalentChannel"])
    equivalentChannelMagnitude.append(caviar_output["equivalentChannelMagnitude"])
    best_ray.append(caviar_output["best_ray"])
    bit_rate.append(caviar_output["bit_rate"])

output_filename = os.path.join(current_dir, "bit_rates.npz")
rx_airsim_position = np.array(rx_airsim_position)
rx_starting_position = np.array(rx_starting_position)
rx_current_position = np.array(rx_current_position)
mimoChannel = np.array(mimoChannel)
equivalentChannel = np.array(equivalentChannel)
equivalentChannelMagnitude = np.array(equivalentChannelMagnitude)
best_ray = np.array(best_ray, dtype=object)
bit_rate = np.array(bit_rate)

np.savez(
    output_filename,
    rx_airsim_position=rx_airsim_position,
    rx_starting_position=rx_starting_position,
    rx_current_position=rx_current_position,
    mimoChannel=mimoChannel,
    equivalentChannel=equivalentChannel,
    equivalentChannelMagnitude=equivalentChannelMagnitude,
    best_ray=best_ray,
    bit_rate=bit_rate,
)
