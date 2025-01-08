import airsim
import csv
import time
import os
import numpy as np
import math
import sys

sys.path.append("./")
import caviar_config


def airsim_connect(ip):
    client = airsim.MultirotorClient(ip)
    client.confirmConnection()
    return client


def airsim_moveToInitialPosition(client):
    client.moveToPositionAsync(0, 0, 0, 1).join()


def airsim_takeoff(client, uav_id):
    client.enableApiControl(True, uav_id)
    client.armDisarm(True, uav_id)
    client.takeoffAsync(vehicle_name=uav_id).join()


def airsim_takeoff_all(client):
    for uav in caviar_config.drone_ids:
        airsim_takeoff(client, uav)


def airsim_reset(client):
    client.reset()


def airsim_land(client, uav_id):
    landed = client.getMultirotorState(vehicle_name=uav_id).landed_state
    if landed == airsim.LandedState.Landed:
        print("already landed...")
    else:
        client.armDisarm(False, uav_id)
    client.enableApiControl(False, uav_id)


def airsim_land_all(client):
    for uav in caviar_config.drone_ids:
        airsim_land(client, uav)


def move_on_path(client, uav, path, speed=5):
    path_list = []

    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        csv_reader.__next__()

        for row in csv_reader:
            path_list.append(
                airsim.Vector3r(float(row[0]), float(row[1]), float(row[2]))
            )

    client.enableApiControl(True, uav)
    client.moveOnPathAsync(
        path_list,
        speed,
        3e38,
        airsim.DrivetrainType.ForwardOnly,
        airsim.YawMode(False, 0),
        vehicle_name=uav,
    )


def info_csv(user_id, episode):
    with open("./episodes/ep{}.csv".format(episode)) as cs:
        episode_data = csv.DictReader(cs)
        info = []
        for row in episode_data:
            if row["obj"] == user_id:
                values = list(row.values())
                tmp_info = str(",".join(values))
                info.append(tmp_info)
    return iter(info)


def positions_csv(user_id, episode):
    with open("./episodes/ep{}.csv".format(episode)) as cs:
        episode_data = csv.DictReader(cs)
        output = []
        for row in episode_data:
            if row["obj"] == user_id:
                xyz = ("{},{},{}").format(row["pos_x"], row["pos_y"], row["pos_z"])
                output.append(xyz)
    return iter(output)


def move_to_point(client, uav, x, y, z, speed=5):
    client.enableApiControl(True)
    client.moveToPositionAsync(
        x,
        y,
        z,
        speed,
        3e38,
        airsim.DrivetrainType.ForwardOnly,
        airsim.YawMode(False, 0),
        vehicle_name=uav,
    )


def has_uav_arrived(client, uav, x, y, z):
    uav_pose = airsim_getpose(client, uav)
    if (
        math.isclose(uav_pose[0], x, abs_tol=0.5)
        and math.isclose(uav_pose[1], y, abs_tol=0.5)
        and math.isclose(uav_pose[2], z, abs_tol=0.6)
    ):
        return True
    else:
        return False


def airsim_getpose(client, uav_id):
    coordinates = client.getMultirotorState(
        vehicle_name=uav_id
    ).kinematics_estimated.position.to_numpy_array()
    return coordinates


def airsim_getpose_offset(client, uav_id):
    coordinates = client.getMultirotorState(
        vehicle_name=uav_id
    ).kinematics_estimated.position.to_numpy_array()
    coordinates_offset = np.add(coordinates, caviar_config.initial_pose_offset)
    return coordinates_offset


def airsim_getorientation(client, uav_id):
    orientation = client.getMultirotorState(
        vehicle_name=uav_id
    ).kinematics_estimated.orientation.to_numpy_array()
    return orientation


def airsim_getangularacc(client, uav_id):
    acc = client.getMultirotorState(
        vehicle_name=uav_id
    ).kinematics_estimated.angular_acceleration.to_numpy_array()
    return acc


def airsim_getangularvel(client, uav_id):
    vel = client.getMultirotorState(
        vehicle_name=uav_id
    ).kinematics_estimated.angular_velocity.to_numpy_array()
    return vel


def airsim_getlinearacc(client, uav_id):
    acc = client.getMultirotorState(
        vehicle_name=uav_id
    ).kinematics_estimated.linear_acceleration.to_numpy_array()
    return acc


def airsim_getlinearvel(client, uav_id):
    vel = client.getMultirotorState(
        vehicle_name=uav_id
    ).kinematics_estimated.linear_velocity.to_numpy_array()
    return vel


def airsim_gettimestamp(client, uav_id):
    timestamp = client.getMultirotorState(vehicle_name=uav_id).timestamp
    return timestamp


def airsim_getcollision(client, uav_id):
    collision = client.getMultirotorState(vehicle_name=uav_id).collision.has_collided
    return collision


def airsim_setpose(client, uav_id, x, y, z, orien_x, orien_y, orien_z, orien_w):
    success = client.simSetVehiclePose(
        airsim.Pose(
            airsim.Vector3r(x, y, z),
            airsim.Quaternionr(
                x_val=orien_x, y_val=orien_y, z_val=orien_z, w_val=orien_w
            ),
        ),
        True,
        vehicle_name=uav_id,
    )
    return success


def airsim_setpose_offset(client, uav_id, x, y, z, orien_x, orien_y, orien_z, orien_w):
    x = x - caviar_config.initial_pose_offset[0]
    y = y - caviar_config.initial_pose_offset[1]
    z = z - caviar_config.initial_pose_offset[2]
    success = client.simSetVehiclePose(
        airsim.Pose(
            airsim.Vector3r(x, y, z),
            airsim.Quaternionr(
                x_val=orien_x, y_val=orien_y, z_val=orien_z, w_val=orien_w
            ),
        ),
        True,
        vehicle_name=uav_id,
    )
    return success


def unreal_getpose(client, obj_id):
    coordinates = client.simGetObjectPose(obj_id).position.to_numpy_array()
    return coordinates


def unreal_getorientation(client, obj_id):
    orientation = client.simGetObjectPose(obj_id).orientation.to_numpy_array()
    return orientation


def unreal_setpose(client, obj_id, x, y, z, orien_x, orien_y, orien_z, orien_w):
    success = client.simSetObjectPose(
        obj_id,
        airsim.Pose(
            airsim.Vector3r(x, y, z),
            airsim.Quaternionr(
                x_val=orien_x, y_val=orien_y, z_val=orien_z, w_val=orien_w
            ),
        ),
        True,
    )
    return success


def unreal_plotbeam(client, distance, azimuth, elevation, duration):
    success = client.simRunConsoleCommand(
        "ke caviar_base_station plot_beam "
        + str(distance)
        + " "
        + str(azimuth)
        + " "
        + str(elevation)
        + " "
        + str(duration)
        + " (R=0.9, G=0.45, B=0.0, A=1.0)"
    )
    return success


def unreal_plotbeam_best(client, distance, azimuth, elevation, duration):
    success = client.simRunConsoleCommand(
        "ke caviar_base_station plot_beam "
        + str(distance)
        + " "
        + str(azimuth)
        + " "
        + str(elevation)
        + " "
        + str(duration)
        + " (R=0.26, G=0.52, B=0.96, A=1.0)"
    )
    return success


def unreal_plotbox(client, actor, duration):
    success = client.simRunConsoleCommand(
        "ke caviar_base_station plot_box " + str(actor) + " " + str(duration)
    )
    return success


def airsim_save_images(client, record_path="./"):
    for uav in caviar_config.drone_ids:
        png_image = client.simGetImage("0", airsim.ImageType.Scene, vehicle_name=uav)
        airsim.write_file(
            os.path.normpath(record_path + uav + "_" + str(time.time()) + ".png"),
            png_image,
        )


def airsim_save_external_images(client, record_path="./", cam="0"):
    if not os.path.exists(record_path):
        os.mkdir(record_path)

    multimodal_output_folder = os.path.join(record_path, "multimodal")

    if not os.path.exists(multimodal_output_folder):
        os.mkdir(multimodal_output_folder)

    if caviar_config.panoramic:
        image_side = 0
        for pose in caviar_config.cam_poses:
            image_side = image_side + 1
            for cam_type in caviar_config.cam_types:
                client.simSetCameraPose(
                    cam, pose, vehicle_name=caviar_config.drone_ids[0], external=True
                )
                png_image = client.simGetImage(
                    cam,
                    cam_type,
                    vehicle_name=caviar_config.drone_ids[0],
                    external=True,
                )
                cam_type_path = os.path.join(multimodal_output_folder, str(cam_type))
                if not os.path.exists(cam_type_path):
                    os.mkdir(cam_type_path)
                record_file = os.path.join(
                    cam_type_path,
                    caviar_config.drone_ids[0]
                    + "_"
                    + str(image_side)
                    + "_"
                    + str(time.time())
                    + ".png",
                )
                airsim.write_file(
                    os.path.normpath(record_file),
                    png_image,
                )
    else:
        for cam_type in caviar_config.cam_types:
            png_image = client.simGetImage(
                cam, cam_type, vehicle_name=caviar_config.drone_ids[0], external=True
            )
            cam_type_path = os.path.join(multimodal_output_folder, str(cam_type))
            if not os.path.exists(cam_type_path):
                os.mkdir(cam_type_path)
            record_file = os.path.join(
                cam_type_path,
                caviar_config.drone_ids[0] + "_" + str(time.time()) + ".png",
            )
            airsim.write_file(
                os.path.normpath(record_file),
                png_image,
            )


def airsim_getimages(client, uav_id):
    image = client.simGetImage(0, airsim.ImageType.Scene, vehicle_name=uav_id)
    return image


def linecount(eps):
    if len(eps) < 2:
        all_eps = [int(eps[0])]
    else:
        all_eps = list(range(int(eps[0]), int(eps[1]) + 1))
    count = 0
    for ep in all_eps:
        episode_file = open(f"./episodes/ep{int(ep)}.csv", "r")
        for line in episode_file:
            line = line.split(",")
            if line[1] == "uav1":
                count += 1
        episode_file.close()
    return count


def addPedestriansOnPath(client, path):
    path_list = []

    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        csv_reader.__next__()
        for column in csv_reader:
            path_list.append(
                airsim.Vector3r(float(column[0]), float(column[1]), float(135.81))
            )
    if len(path_list) - 2 > len(caviar_config.pedestrians):
        print(
            "The number of pedestrian objects should be lower than the number of waypoints"
        )
    else:
        for i in range(len(caviar_config.pedestrians)):
            client.simSetObjectPose(
                caviar_config.pedestrians[i],
                airsim.Pose(path_list[i + 1], airsim.to_quaternion(0, 0, 0)),
                True,
            )
            client.simSetObjectScale(
                caviar_config.pedestrians[i], airsim.Vector3r(3, 3, 3)
            )
