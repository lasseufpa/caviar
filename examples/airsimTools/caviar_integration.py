import caviar_config
import caviar_tools
import time
import os
import cv2
import csv
from pynats import NATSClient
import json
import numpy as np
import airsim

def convertPositionFromAirSimToSionna(x, y, z):
    # Sionna coordinates for AirSim PlayerStart position (AirSim's origin point)
    # Central Park offset
    offset = {"x": 23.34, "y": -3.42, "z": 137.23}
    return [offset["x"] + x, offset["y"] - y, offset["z"] - z]

## REMOVE AFTER EXPERIMENT
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
#########################

inloop = True

sionna_finished_runnning = True

current_throughput = 0

save_multimodal = False

rescued_targets = 0

simu_time_of_rescue = []
simu_pose_of_rescue = []
throughputs_during_rescue = []
times_waited_during_rescue = []

def get_time_for_rescue(throughput):
    '''
    This function calculates the time for transmit them all and finish 
    the rescue.

    The rescue will finish after transmiting 100 pictures of 4 MB (3.2e7 bits), representing
    a 4K image and a point cloud file made with LiDAR with 2 GB (16e9 bits)
    '''
    tx_max = (3.2e7 * 100)  + (16e9)
    time_to_tx = (tx_max / (throughput))
    return time_to_tx


def addNoise(image, throughput): 
    gaussian_noise = np.zeros(image.shape, np.uint8)

    if throughput < 80 and throughput > 60:
        # PSNR: ~23.585 dB
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Noise level LOW: {throughput}")
        cv2.randn(gaussian_noise, 0, 45)   
    elif throughput <= 60 and throughput > 20:
        # PSNR: ~19.1642 dB
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Noise level MEDIUM: {throughput}")
        cv2.randn(gaussian_noise, 0, 90)
    elif throughput <= 20 and throughput >= 0:
        # PSNR: ~8.1041 dB
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Noise level HIGH: {throughput}")
        cv2.randn(2*gaussian_noise, 0, 270)
        gaussian_noise-100
    else:
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> No Noise level: {throughput}")

    image = cv2.add(image, gaussian_noise)
    return image

with NATSClient() as natsclient:
    # Number of trajectories to be executed
    # Each trajectory is an episode
    n_trajectories = 1
    current_dir = os.getcwd()

    trajectories_files = os.path.join(
        current_dir,
        "examples",
        "airsimTools",
        "waypoints",
        "trajectories",
    )
    # Create a folder to write the UE4 simulation result
    try:
        os.mkdir("./episodes")
    except OSError as error:
        print(error)

    client = caviar_tools.airsim_connect(ip="127.0.0.1")

    #  Socket to talk to server
    natsclient.connect()

    def callback(msg):
        global sionna_finished_runnning
        sionna_finished_runnning = True


    def updateThroughput(msg):
        global current_throughput
        payload = json.loads(msg.payload.decode())
        current_throughput = float(payload['throughput'])
        print(f'----------------------------> CURRENT THROUGHPUT: {current_throughput} Gbps')

    natsclient.subscribe(subject="communications.state", callback=callback)
    natsclient.subscribe(subject="communications.throughput", callback=updateThroughput)

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

        

        caviar_tools.airsim_setpose(
            client, caviar_config.drone_ids[0], -320.34, -198.58, 130, 0, 0, 0, 0
        )
        time.sleep(0.5)

        initial_timestamp = caviar_tools.airsim_gettimestamp(client, caviar_config.drone_ids[0])

        # takeoff and start the UAV trajectory
        caviar_tools.airsim_takeoff_all(client)
        time.sleep(1)
        caviar_tools.move_to_point(
            client, caviar_config.drone_ids[0], -320.34, -198.58, 128, 10
        )

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
            # Continue the simulation for 100ms
            start_time = time.time()
            
            if inloop:
                if sionna_finished_runnning:
                    client.simContinueForTime(0.10)
                    sionna_finished_runnning = False
            else:
                client.simContinueForTime(0.10)
                # client.simPause(False)
            natsclient.wait(count=1)
            

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
                rawimg = caviar_tools.airsim_getimages(
                    client, caviar_config.drone_ids[0]
                )
                img = cv2.imdecode(airsim.string_to_uint8_array(rawimg), cv2.IMREAD_COLOR)
                height, width, depth = img.shape
                # img_size_bits = height * width * depth * 8 # Considering that each channel from a RGB image is represented by 8 bits color depth (0, 255)
                # img_size_bytes = img_size_bits/1024
                # cv2.imshow("window_name", img)
                # print('img_size_bytes: ', img_size_bytes)

                img = addNoise(img, current_throughput)
                
                ## REMOVE AFTER EXPERIMENT
                results = model.predict(source=img, classes=0, save=True, save_txt=True)  # save predictions as labels
                try:
                    print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Detected class: {results[0].boxes.data[0,5]}')
                    print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Human detected probability: {results[0].boxes.data[0,4]}')
                    target_is_detected = results[0].boxes.data[0,5] == 0
                    if target_is_detected:
                        rescue_time = get_time_for_rescue(current_throughput*1e9)
                        throughputs_during_rescue.append(current_throughput)
                        times_waited_during_rescue.append(rescue_time)
                        client.simDestroyObject(caviar_config.pedestrians[actualWaypoint-1])
                        print(f"@@@@@@@ get_time_for_rescue(current_throughput): {rescue_time}")
                        time.sleep(rescue_time)
                        rescued_targets = rescued_targets + 1
                        simu_time_of_rescue.append((airsim_timestamp-initial_timestamp)*1e-9)
                        simu_pose_of_rescue.append(convertPositionFromAirSimToSionna(uav_pose[0],uav_pose[1],uav_pose[2]))
                except:
                    print("NO DETECTION")
                #########################

                natsclient.publish(
                    subject="3D.mobility.positions",
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

                    print("Compute best beam")
                    print("get transmission delay for 10 images")

                    print("wait")

                    caviar_tools.move_to_point(
                        client,
                        uav,
                        path_list[actualWaypoint][0],
                        path_list[actualWaypoint][1],
                        path_list[actualWaypoint][2],
                    )
                    print(actualWaypoint)

                    if actualWaypoint == (len(path_list) - 7):
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

            output_folder = os.path.join(os.getcwd(), "runs")
            if save_multimodal:
                caviar_tools.airsim_save_external_images(client, output_folder, "FixedCamera1")
            # Get an write information about others objects in the simulation (cars and pedestrians). Each object is described in the configuration file (caviar_config.py)
            for obj in caviar_config.ue_objects:
                object_pose = caviar_tools.unreal_getpose(client, obj)
                object_orien = caviar_tools.unreal_getorientation(client, obj)
            end_time = time.time()
            print(f"CAVIAR in-loop step duration (seconds): {end_time-start_time}")
            print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Simulation duration (seconds): {(airsim_timestamp-initial_timestamp)*1e-9}")

        print(f"Total mission time: {(airsim_timestamp-initial_timestamp)*1e-9}")
        print(f"Rescued targets: {rescued_targets}")
        np.savez(
            "mission_log.npz",
            total_mission_time=(airsim_timestamp-initial_timestamp)*1e-9,
            rescued_targets=rescued_targets,
            simu_time_of_rescue=simu_time_of_rescue,
            simu_pose_of_rescue=simu_pose_of_rescue,
            throughputs_during_rescue=throughputs_during_rescue,
            times_waited_during_rescue=times_waited_during_rescue
        )