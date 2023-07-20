import csv
import os


def convertPositionFromAirSimToSionna(x, y, z):
    # Sionna coordinates for AirSim PlayerStart position (AirSim's origin point)
    # Central Park offset
    offset = {"x": 23.34, "y": -3.42, "z": 137.23}
    return [offset["x"] + x, offset["y"] - y, offset["z"] - z]


def readPaths(path):
    path_list = []

    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        csv_reader.__next__()
        for column in csv_reader:
            path_list.append(
                convertPositionFromAirSimToSionna(
                    float(column[0]), float(column[1]), float(column[2])
                )
            )

    return path_list


current_dir = os.getcwd()
trajectories_files = os.path.join(
    current_dir,
    "examples",
    "airsimTools",
    "waypoints",
    "trajectories",
)
num_paths = 10
converted_paths = []
for path_id in range(num_paths):
    converted_paths.append(
        readPaths(os.path.join(trajectories_files, "path" + str(path_id) + ".csv"))
    )
# [-153.66, 128.93, 77.22999999999999]
# [-134.66, 118.48, 77.22999999999999]
# [-113.66, 106.92999999999999, 77.22999999999999]
# [-46.66, 70.08, 77.22999999999999]
# [-16.66, 124.63000000000001, 77.22999999999999]
# [-46.66, 70.08, 77.22999999999999]
# [143.34, -34.42, 77.22999999999999]
print("END")
