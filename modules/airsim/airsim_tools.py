import csv
import logging
import math
import os
import sys
import time

import airsim
import numpy as np

from kernel.logger import LOGGER, logging

logging.getLogger("tornado.general").setLevel(logging.ERROR)
sys.path.append("./")


class AirSimTools:
    client = None

    def airsim_connect(self, ip: str = "127.0.0.1", timeout: float = 20.0):
        start_time = time.time()
        while True:
            try:
                if timeout > time.time() - start_time:
                    self.client = airsim.MultirotorClient(ip=ip, timeout_value=timeout)
                    self.client.confirmConnection()
                    time.sleep(1)
                break
            except Exception as e:
                time.sleep(1)
                if timeout < time.time() - start_time:
                    break

    def airsim_moveToInitialPosition(self, client):
        client.moveToPositionAsync(0, 0, 0, 1).join()

    def airsim_takeoff(self):
        if self.client:
            self.client.enableApiControl(True)
            self.client.armDisarm(True)
            self.client.takeoffAsync().join()

    """
    def airsim_takeoff_all(self, client):
        for uav in caviar_config.drone_ids:
            airsim(client, uav)
    """

    def airsim_reset(self, client):
        client.reset()

    def airsim_land(self, client, uav_id):
        landed = client.getMultirotorState(vehicle_name=uav_id).landed_state
        if landed == airsim.LandedState.Landed:
            print("already landed...")
        else:
            client.armDisarm(False, uav_id)
        client.enableApiControl(False, uav_id)

    """
    def airsim_land_all(self, client):
        for uav in caviar_config.drone_ids:
            self.airsim_land(client, uav)
    """

    def move_on_path(self, paths: list, speed=5):
        path_list = []
        for path in paths:
            path_list.append(
                airsim.Vector3r(float(path[0]), float(path[1]), float(path[2]))
            )

        self.client.enableApiControl(True)
        time.sleep(
            0.5
        )  # @TODO: I don't know why but drone only works after adding this delay
        self.client.moveOnPathAsync(
            path_list,
            speed,
            3e38,
            airsim.DrivetrainType.ForwardOnly,
            airsim.YawMode(False, 0),
            # vehicle_name=uav,
        )

    def pause(self):
        """
        Pauses the execution for a specified time.
        """
        self.client.simPause(True)

    def resume(self):
        """
        Resumes the execution
        """
        self.client.simPause(False)

    def info_csv(self, user_id, episode):
        with open("./episodes/ep{}.csv".format(episode)) as cs:
            episode_data = csv.DictReader(cs)
            info = []
            for row in episode_data:
                if row["obj"] == user_id:
                    values = list(row.values())
                    tmp_info = str(",".join(values))
                    info.append(tmp_info)
        return iter(info)

    def positions_csv(self, user_id, episode):
        with open("./episodes/ep{}.csv".format(episode)) as cs:
            episode_data = csv.DictReader(cs)
            output = []
            for row in episode_data:
                if row["obj"] == user_id:
                    xyz = ("{},{},{}").format(row["pos_x"], row["pos_y"], row["pos_z"])
                    output.append(xyz)
        return iter(output)

    def move_to_point(self, x: float, y: float, z: float, speed: float = 5.0):
        self.client.enableApiControl(True)
        self.client.moveToPositionAsync(
            x,
            y,
            z,
            speed,
            3e38,
            airsim.DrivetrainType.ForwardOnly,
            airsim.YawMode(False, 0),
        )

    def has_uav_arrived(self, client, uav, x, y, z):
        uav_pose = self.airsim_getpose(client, uav)
        if (
            math.isclose(uav_pose[0], x, abs_tol=0.5)
            and math.isclose(uav_pose[1], y, abs_tol=0.5)
            and math.isclose(uav_pose[2], z, abs_tol=0.6)
        ):
            return True
        else:
            return False

    def airsim_getpose(self):  # uav_id):
        coordinates = self.client.getMultirotorState(
            # vehicle_name=uav_id
        ).kinematics_estimated.position.to_numpy_array()
        return coordinates

    """
    def airsim_getpose_offset(self, client, uav_id):
        coordinates = client.getMultirotorState(
            vehicle_name=uav_id
        ).kinematics_estimated.position.to_numpy_array()
        coordinates_offset = np.add(coordinates, caviar_config.initial_pose_offset)
        return coordinates_offset
    """

    def airsim_getorientation(self, client, uav_id):
        orientation = client.getMultirotorState(
            vehicle_name=uav_id
        ).kinematics_estimated.orientation.to_numpy_array()
        return orientation

    def airsim_getangularacc(self, client, uav_id):
        acc = client.getMultirotorState(
            vehicle_name=uav_id
        ).kinematics_estimated.angular_acceleration.to_numpy_array()
        return acc

    def airsim_getangularvel(self, client, uav_id):
        vel = client.getMultirotorState(
            vehicle_name=uav_id
        ).kinematics_estimated.angular_velocity.to_numpy_array()
        return vel

    def airsim_getlinearacc(self):  # , uav_id
        acc = self.client.getMultirotorState(
            # vehicle_name=uav_id
        ).kinematics_estimated.linear_acceleration.to_numpy_array()
        return acc

    def airsim_getlinearvel(self):  # , client, uav_id
        vel = self.client.getMultirotorState(
            # vehicle_name=uav_id
        ).kinematics_estimated.linear_velocity.to_numpy_array()
        return vel

    def airsim_gettimestamp(self, client, uav_id):
        timestamp = client.getMultirotorState(vehicle_name=uav_id).timestamp
        return timestamp

    def airsim_getcollision(
        self,  # client, uav_id
    ):
        collision = self.client.getMultirotorState(
            # vehicle_name=uav_id
        ).collision.has_collided
        return collision

    def is_drone_moving(self, threshold=0.15):
        """
        Checks if the drone is moving by analyzing its linear velocity.

        @param client: The AirSim client instance.
        @param uav_id: The ID of the drone to check.
        @param threshold: The velocity threshold below which the drone is considered stationary.
        @return: True if the drone is moving, False otherwise.
        """
        linear_velocity = self.airsim_getlinearvel()  # self.client, uav_id
        speed = np.linalg.norm(
            linear_velocity
        )  # Calculate the magnitude of the velocity vector
        return speed > threshold

    def airsim_setpose(
        self,
        x,
        y,
        z,
        orien_x=0,
        orien_y=0,
        orien_z=0,
        orien_w=0,  # uav_id,
    ):
        success = self.client.simSetVehiclePose(
            airsim.Pose(
                airsim.Vector3r(x, y, z),
                airsim.Quaternionr(
                    x_val=orien_x, y_val=orien_y, z_val=orien_z, w_val=orien_w
                ),
            ),
            True,
            # vehicle_name=uav_id,
        )
        return success

    """
    def airsim_setpose_offset(
        self, client, uav_id, x, y, z, orien_x, orien_y, orien_z, orien_w
    ):
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
    """

    def unreal_getpose(self, client, obj_id):
        coordinates = client.simGetObjectPose(obj_id).position.to_numpy_array()
        return coordinates

    def unreal_getorientation(self, client, obj_id):
        orientation = client.simGetObjectPose(obj_id).orientation.to_numpy_array()
        return orientation

    def unreal_setpose(
        self, client, obj_id, x, y, z, orien_x, orien_y, orien_z, orien_w
    ):
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

    def unreal_plotbeam(self, client, distance, azimuth, elevation, duration):
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

    def unreal_plotbeam_best(self, client, distance, azimuth, elevation, duration):
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

    def unreal_plotbox(self, client, actor, duration):
        success = client.simRunConsoleCommand(
            "ke caviar_base_station plot_box " + str(actor) + " " + str(duration)
        )
        return success

    """
    def airsim_save_images(self, client, record_path="./"):
        for uav in caviar_config.drone_ids:
            png_image = client.simGetImage(
                "0", airsim.ImageType.Scene, vehicle_name=uav
            )
            airsim.write_file(
                os.path.normpath(record_path + uav + "_" + str(time.time()) + ".png"),
                png_image,
            )

    def airsim_save_external_images(self, client, record_path="./", cam="0"):
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
                        cam,
                        pose,
                        vehicle_name=caviar_config.drone_ids[0],
                        external=True,
                    )
                    png_image = client.simGetImage(
                        cam,
                        cam_type,
                        vehicle_name=caviar_config.drone_ids[0],
                        external=True,
                    )
                    cam_type_path = os.path.join(
                        multimodal_output_folder, str(cam_type)
                    )
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
                    caviar_config.drone_ids[0] + "_" + str(time.time()) + ".png",
                )
                airsim.write_file(
                    os.path.normpath(record_file),
                    png_image,
                )
    """

    def airsim_getimages(self, client, uav_id):
        image = client.simGetImage(0, airsim.ImageType.Scene, vehicle_name=uav_id)
        return image

    def linecount(self, eps):
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

    """
    def addPedestriansOnPath(self, client, path):
        path_list = []

        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            csv_reader.__next__()
            for column in csv_reader:
                path_list.append(
                    airsim.Vector3r(float(column[0]), float(column[1]), float(135.81))
                )
        if len(caviar_config.pedestrians) > len(path_list):
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
    """
