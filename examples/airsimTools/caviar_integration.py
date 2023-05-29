import caviar_config
import caviar_tools
import time
import os
import cv2
import csv
from pynats import NATSClient


with NATSClient() as natsclient:
    # Number of trajectories to be executed
    # Each trajectory is an episode
    n_trajectories = 500
    current_dir = os.getcwd()

    trajectories_files = os.path.join(
        current_dir,
        "examples",
        "airsimTools",
        "waypoints",
        "trajectories",
    )

    # Creat a folder to write the UE4 simulation result
    try:
        os.mkdir("./episodes")
    except OSError as error:
        print(error)

    client = caviar_tools.airsim_connect(ip="127.0.0.1")

    #  Socket to talk to server
    natsclient.connect()

    def callback(msg):
        #print(f"Received a message with subject {msg.subject}: {msg}")

    natsclient.subscribe(subject="caviar.su.sionna.state", callback=callback)

    for episode in range(n_trajectories):
        print("Episode: " + str(episode))

        # Save the actual time to compute the run-time at the end of the episode
        initial_time = time.time()

        isFinished = False

        # Delay between episodes to avoid crashs
        time.sleep(1)

        caviar_tools.addPedestriansOnPath(
            client, os.path.join(trajectories_files, "path" + str(episode) + ".csv")
        )

        # Reset the airsim simulation
        caviar_tools.airsim_reset(client)

        # takeoff and start the UAV trajectory
        caviar_tools.airsim_takeoff_all(client)

        caviar_tools.move_to_point(client, caviar_config.drone_ids[0], 0, 0, -22, 10)

        path_list = []

        with open(
            os.path.join(trajectories_files, "path" + str(episode) + ".csv")
        ) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            csv_reader.__next__()
            for row in csv_reader:
                path_list.append([float(row[0]), float(row[1]), float(row[2])])
        actualWaypoint = 0

        # Pause the simulation
        client.simPause(True)
        while not (isFinished):
            # Continue the simulation for 10ms
            start_time = time.time()
            natsclient.wait(count=1)
            client.simContinueForTime(0.10)

            # Get information about each UAV in the configuration file (caviar_config.py)
            for uav in caviar_config.drone_ids:
                uav_pose = caviar_tools.airsim_getpose(client, uav)
                uav_orien = caviar_tools.airsim_getorientation(client, uav)
                uav_linear_acc = caviar_tools.airsim_getlinearacc(client, uav)
                uav_linear_vel = caviar_tools.airsim_getlinearvel(client, uav)
                uav_angular_acc = caviar_tools.airsim_getangularacc(client, uav)
                uav_angular_vel = caviar_tools.airsim_getangularvel(client, uav)
                airsim_timestamp = caviar_tools.airsim_gettimestamp(client, uav)

                # Get frames
                # rawimg = caviar_tools.airsim_getimages(
                #     client, caviar_config.drone_ids[0]
                # )
                # img = cv2.imdecode(airsim.string_to_uint8_array(rawimg), cv2.IMREAD_COLOR)
                # height, width, depth = img.shape
                # img_size_bits = height * width * depth * 8 # Considering that each channel from a RGB image is represented by 8 bits color depth (0, 255)
                # img_size_bytes = img_size_bits/1024
                # cv2.imshow("window_name", img)
                # print('img_size_bytes: ', img_size_bytes)

                natsclient.publish(
                    subject="caviar.ue.mobility.positions",
                    payload=b'{"UE_type":"UAV","UE_Id":'
                    + b'"'
                    + str(uav).encode()
                    + b'"'
                    + b',"timestamp":'
                    + b'"'
                    + str(airsim_timestamp).encode()
                    + b'"'
                    + b',"position": {"x":'
                    + str(uav_pose[0]).encode()
                    + b',"y":'
                    + str(uav_pose[1]).encode()
                    + b',"z":'
                    + str(uav_pose[2]).encode()
                    + b"}}",
                )

                # Check if the UAV is landed or has collided and finish the episode
                if caviar_tools.airsim_getcollision(client, uav):
                    client.simPause(False)
                    isFinished = True
                    print(
                        "Episode "
                        + str(episode)
                        + " concluded with "
                        + str(time.time() - initial_time)
                        + "s"
                    )
                # Verify actual position
                if caviar_tools.has_uav_arrived(
                    client,
                    uav,
                    path_list[actualWaypoint][0],
                    path_list[actualWaypoint][1],
                    path_list[actualWaypoint][2],
                ):
                    actualWaypoint = actualWaypoint + 1
                    # Add here the YOLO for object detection

                    caviar_tools.move_to_point(
                        client,
                        caviar_config.drone_ids[0],
                        path_list[actualWaypoint][0],
                        path_list[actualWaypoint][1],
                        path_list[actualWaypoint][2],
                    )

                    if actualWaypoint == (len(path_list) - 1):
                        client.simPause(False)
                        caviar_tools.airsim_land_all(client)
                        isFinished = True
                        print(
                            "Episode "
                            + str(episode)
                            + " concluded with "
                            + str(time.time() - initial_time)
                            + "s"
                        )

            # Get an write information about others objects in the simulation (cars and pedestrians). Each object is described in the configuration file (caviar_config.py)
            for obj in caviar_config.ue_objects:
                object_pose = caviar_tools.unreal_getpose(client, obj)
                object_orien = caviar_tools.unreal_getorientation(client, obj)
            end_time = time.time()
            print(f"Step duration: {end_time-start_time}")
