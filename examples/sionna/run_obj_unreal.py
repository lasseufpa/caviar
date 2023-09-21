import airsim
# import time
from convertAirsimPathToSionna import convertPositionFromSionnatoUnreal
import numpy as np

def plot_beam_interaction(filepath, duration=0.5):
    client = airsim.MultirotorClient()
    # init_time = time.time()
    with open(filepath, "r") as run:
        lines = run.readlines()
    
    file = []
    for line in lines:
        file.append(line.rstrip())

    list_with_values = []

    for line in file:
        if line.startswith("v"):
            list_with_values.append(line[2:])

    list_of_lists = [value.split() for value in list_with_values]

    converted_list = [convertPositionFromSionnatoUnreal(np.array(sublist, dtype=np.float32).tolist()) for sublist in list_of_lists]

    # end_time = time.time()

    # print(f"Total time: {(end_time - init_time)*1e3} ms")

    for i in range(len(converted_list)-1):
        client.simRunConsoleCommand(
            f"ke * plot_raytrace {list_with_values[i]} {list_with_values[i+1]} {duration}"
        )

    """for i in range(len(converted_list)):
        client.simRunConsoleCommand(f'ke * plot_raytrace {list_with_values[i]} {list_with_values[i+1]} {duration}')
    """
