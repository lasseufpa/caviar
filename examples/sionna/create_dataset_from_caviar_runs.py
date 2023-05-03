import numpy as np
import os

dataset_dir_name = "runs01"
current_dir = os.getcwd()
dataset_dir = os.path.join(current_dir, dataset_dir_name)

# Iterate over all npz and create one big npz to separate into data and label

############################ Example of creating a npz
# np.savez(
#         output_filename,
#         path_coefficients=a,
#         path_delays=tau,
#         rx_airsim_position=[new_x, new_y, new_z],
#         rx_starting_position=[rx_starting_x, rx_starting_y, rx_starting_z],
#         rx_current_position=[rx_current_x, rx_current_y, rx_current_z],
#         mimoChannel=mimoChannel,
#         equivalentChannel=equivalentChannel,
#         equivalentChannelMagnitude=equivalentChannelMagnitude,
#         best_ray=best_ray,
#     )

############################ Example of loading a npz
# caviar_output = np.load("/home/joao/Downloads/run_1683048632505798144.npz")

############################ Example of accessing data from inside a npz
# rx_airsim_position=caviar_output["rx_airsim_position"],
# rx_starting_position=caviar_output["rx_starting_position"],
# rx_current_position=caviar_output["rx_current_position"],
# mimoChannel=caviar_output["mimoChannel"]
# equivalentChannel=caviar_output["equivalentChannel"]
# equivalentChannelMagnitude=caviar_output["equivalentChannelMagnitude"]
# best_ray=caviar_output["best_ray"]

print("END")
