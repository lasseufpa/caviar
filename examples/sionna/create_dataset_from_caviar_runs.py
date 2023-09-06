import numpy as np
import os
from os import listdir
from joblib import load
enc = load("trained_encoder_v6.joblib")

current_dir = os.getcwd()
dataset_dir = os.path.join(current_dir, "runs")

rx_airsim_position = []
rx_starting_position = []
rx_current_position = []
mimoChannel = []
equivalentChannel = []
equivalentChannelMagnitude = []
best_ray = []
bit_rate = []
best_bit_rate_Gbps = []
random_bit_rate_Gbps = []

onlynpz = [file for file in listdir(dataset_dir) if file[-3:] == "npz"]
for i in range(len(onlynpz)):
    dataset_file_name = str(onlynpz[i])
    dataset_file = os.path.join(dataset_dir, dataset_file_name)
    caviar_output = np.load(dataset_file, allow_pickle=True)

    current_ray = caviar_output["best_ray"]
    current_ray_true = [str([current_ray[0][0], current_ray[0][1]])]
    encoded_current_ray = enc.transform(current_ray_true)

    rx_airsim_position.append(caviar_output["rx_airsim_position"])
    rx_starting_position.append(caviar_output["rx_starting_position"])
    rx_current_position.append(caviar_output["rx_current_position"])
    mimoChannel.append(caviar_output["mimoChannel"])
    equivalentChannel.append(caviar_output["equivalentChannel"])
    equivalentChannelMagnitude.append(caviar_output["equivalentChannelMagnitude"])
    best_ray.append(caviar_output["best_ray"])
    bit_rate.append(caviar_output["bit_rate"])
    best_bit_rate_Gbps.append(caviar_output["best_bit_rate_Gbps"])
    random_bit_rate_Gbps.append(caviar_output["random_bit_rate_Gbps"])

    # if encoded_current_ray != 137 and encoded_current_ray != 129:
    # if encoded_current_ray != 63 and encoded_current_ray != 106 and encoded_current_ray != 225:
        # rx_airsim_position.append(caviar_output["rx_airsim_position"])
        # rx_starting_position.append(caviar_output["rx_starting_position"])
        # rx_current_position.append(caviar_output["rx_current_position"])
        # mimoChannel.append(caviar_output["mimoChannel"])
        # equivalentChannel.append(caviar_output["equivalentChannel"])
        # equivalentChannelMagnitude.append(caviar_output["equivalentChannelMagnitude"])
        # best_ray.append(caviar_output["best_ray"])
        # bit_rate.append(caviar_output["bit_rate"])
        # best_bit_rate_Gbps.append(caviar_output["best_bit_rate_Gbps"])
        # random_bit_rate_Gbps.append(caviar_output["random_bit_rate_Gbps"])

output_filename = os.path.join(current_dir, "new_test_set4.npz")
# output_filename = os.path.join(current_dir, "new_test_set3.npz")
rx_airsim_position = np.array(rx_airsim_position)
rx_starting_position = np.array(rx_starting_position)
rx_current_position = np.array(rx_current_position)
mimoChannel = np.array(mimoChannel)
equivalentChannel = np.array(equivalentChannel)
equivalentChannelMagnitude = np.array(equivalentChannelMagnitude)
best_ray = np.array(best_ray)
bit_rate = np.array(bit_rate)
best_bit_rate_Gbps = np.array(best_bit_rate_Gbps)
random_bit_rate_Gbps = np.array(random_bit_rate_Gbps)

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
    best_bit_rate_Gbps=best_bit_rate_Gbps,
    random_bit_rate_Gbps=random_bit_rate_Gbps
)
