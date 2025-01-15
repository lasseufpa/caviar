import csv
import numpy as np


def convertPositionFromAirSimToSionna(x, y, z):
    # Sionna coordinates for AirSim PlayerStart position (AirSim's origin point)
    # Central Park offset
    offset = {"x": 26.50, "y": -0.3, "z": 144.62000977}
    return [offset["x"] + x, offset["y"] - y, offset["z"] - z]


def convertPositionFromSionnaToAirSim(x, y, z):
    # Sionna coordinates for AirSim PlayerStart position (AirSim's origin point)
    # Central Park offset
    offset = {"x": 26.50, "y": -0.3, "z": 144.62000977}
    return [(x - offset["x"]) * 100, (y + offset["y"]) * -100, (z - offset["z"]) * 100]


def convertPositionFromAirSimToUnreal(x, y, z):
    # Unreal coordinates for AirSim PlayerStart position (Unreal's origin point)
    # Central Park offset
    offset = {"x": 0, "y": 0, "z": 14.673}
    scaled_coords = np.multiply([x, y, z], 100).tolist()
    return [
        scaled_coords[0] - offset["x"],
        scaled_coords[1] - offset["y"],
        (-1 * scaled_coords[2]) - offset["z"],
    ]


def convertPositionFromSionnatoUnreal(sionna_coords):
    x = sionna_coords[0]
    y = sionna_coords[1]
    z = sionna_coords[2]
    airsim_coords = convertPositionFromSionnaToAirSim(x, y, z)
    unreal_coords = convertPositionFromAirSimToUnreal(
        x=airsim_coords[0], y=airsim_coords[1], z=airsim_coords[2]
    )
    return unreal_coords


def readPaths(path):
    path_list = []

    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        csv_reader.__next__()
        for column in csv_reader:
            path_list.append(
                convertPositionFromSionnaToAirSim(
                    float(column[0]), float(column[1]), float(column[2])
                )
            )

    return path_list


test_list = [
    [0, 0, 0.05],
    [0, 0, -1.484],
    [1.131, 1.131, -1.457],
    [1.003, 1.003, -9.621],
]

for coordinate in test_list:
    r = convertPositionFromAirSimToUnreal(coordinate[0], coordinate[1], coordinate[2])
    print(r)
