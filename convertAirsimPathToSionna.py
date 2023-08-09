import csv
import os


def convertPositionFromAirSimToSionna(x, y, z):
    # Sionna coordinates for AirSim PlayerStart position (AirSim's origin point)
    # Central Park offset
    offset = {"x": 23.34, "y": -3.42, "z": 137.23}
    return [offset["x"] + x, offset["y"] - y, offset["z"] - z]

def convertPositionFromSionnaToAirSim(x, y, z):
    # Sionna coordinates for AirSim PlayerStart position (AirSim's origin point)
    # Central Park offset
    offset = {"x": 23.34, "y": -3.42, "z": 137.23}
    return [ x - offset["x"], - y - offset["y"], - z - offset["y"]]


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


# current_dir = os.getcwd()
# trajectories_files = os.path.join(
#     current_dir,
#     "examples",
#     "airsimTools",
#     "waypoints",
#     "trajectories",
# )
# num_paths = 10
# converted_paths = []
# for path_id in range(num_paths):
#     converted_paths.append(
#         readPaths(os.path.join(trajectories_files, "path" + str(path_id) + ".csv"))
#     )

test_list = [[-297,202],[-247,176],[-197,156],[-124,110]]

for coordinate in test_list:
    r = convertPositionFromSionnaToAirSim(coordinate[0],coordinate[1],0)
    print(r)