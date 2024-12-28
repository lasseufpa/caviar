import airsim
from examples.sionna.coordinates_converter import convertPositionFromSionnatoUnreal
import numpy as np


def plot_beam_interaction(filepath, duration=0.3):
    client = airsim.MultirotorClient()
    with open(filepath, "r") as run:
        lines = run.readlines()

    file = []
    for line in lines:
        file.append(line.rstrip())

    list_with_values = []
    path = []

    for line in file:
        if line.startswith("v"):
            path.append(line[2:])
        if line.startswith("l"):
            if path != []:
                list_with_values.append(path)
                path = []

    list_of_lists = [[string.split() for string in value] for value in list_with_values]

    converted_list = [
        [
            convertPositionFromSionnatoUnreal(
                np.array(subsublist, dtype=np.float32).tolist()
            )
            for subsublist in sublist
        ]
        for sublist in list_of_lists
    ]

    for path_idx, path in enumerate(converted_list[0]):
        for vertice in range(len(path) - 1):
            client.simRunConsoleCommand(
                f"ke * plot_raytrace {(converted_list[path_idx][vertice][0])-45} {converted_list[path_idx][vertice][1]-692} {(converted_list[path_idx][vertice][2]-27542)} {(converted_list[path_idx][vertice+1][0])-45} {(converted_list[path_idx][vertice+1][1])-692} {(converted_list[path_idx][vertice+1][2]-27542)} {duration}"
            )
