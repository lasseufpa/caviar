import csv
import json
import os
import sys
import time

import airsim
import caviar_tools
import cv2
import numpy as np
import torch
from PIL import Image
from pynats import NATSClient

sys.path.append("./")
import caviar_config
from calc_rescues import get_time_for_rescue

rng = np.random.default_rng(caviar_config.random_seed)


def convertPositionFromAirSimToSionna(x, y, z):
    # Sionna coordinates for AirSim PlayerStart position (AirSim's origin point)
    # Central Park offset
    offset = {"x": 23.34, "y": -3.42, "z": 137.23}
    return [offset["x"] + x, offset["y"] - y, offset["z"] - z]


################################################################################

from caviar_yolo import cfg, device, model, post_proccess, transform
from yolo import draw_bboxes

is_sync = caviar_config.is_sync  # sync(true)/async(false)
is_rescue_mission = caviar_config.is_rescue_mission
simulation_time_step = caviar_config.simulation_time_step  # 500 ms (simulation time)
save_multimodal = caviar_config.save_multimodal

########## INITIALIZATION OF VARIABLES (DO NOT CHANGE THE VALUES) ########
rescue_steps = 0  # in case of a rescue, indicates for how many steps the UAV must wait (keep at zero. Value is updated during execution)
reached_waypoint = False
sionna_finished_running = True
current_throughput = 0
rescued_targets = 0
person_to_be_rescued = False
###########################################################

simu_time_of_rescue = []
simu_pose_of_rescue = []
throughputs_during_rescue = []
times_waited_during_rescue = []


def applyFilter(
    image,
    packet_drop_rate,
    rng=rng,
):
    height = image.shape[0]
    width = image.shape[1]
    n_channels = image.shape[2]
    total_number_of_pixels = height * width * n_channels
    packets_to_drop = int(total_number_of_pixels * packet_drop_rate)
    dropped_package_indexes = rng.choice(
        total_number_of_pixels, packets_to_drop, replace=False
    )
    random_drop_kernel = np.ones(total_number_of_pixels)
    random_drop_kernel[dropped_package_indexes] = 0
    random_drop_kernel = random_drop_kernel.reshape((height, width, n_channels))
    degraded_data = np.multiply(image, random_drop_kernel).astype("uint8")
    degraded_image = Image.fromarray(degraded_data.astype(np.uint8))

    return degraded_image


def addNoise(image, throughput):
    if throughput < 0.09 and throughput > 0.06:
        # PSNR: ~26.3629 dB
        print(f">>>>>>>>>>>>>>>>>>>>> Noise level LOW: {throughput}")
        degraded_image = applyFilter(image, packet_drop_rate=0.01)
    elif throughput <= 0.06 and throughput > 0.03:
        # PSNR: ~12.3902 dB
        print(f">>>>>>>>>>>>>>>>>>>>> Noise level MEDIUM: {throughput}")
        degraded_image = applyFilter(image, packet_drop_rate=0.25)
    elif throughput <= 0.03 and throughput >= 0:
        # PSNR: ~9.376 dB
        print(f">>>>>>>>>>>>>>>>>>>>> Noise level HIGH: {throughput}")
        degraded_image = applyFilter(image, packet_drop_rate=0.5)
    else:
        print(f">>>>>>>>>>>>>>>>>>>>> No Noise level: {throughput}")
        degraded_image = image

    return degraded_image


with NATSClient() as natsclient:

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
        global sionna_finished_running
        sionna_finished_running = True

    def updateThroughput(msg):
        global current_throughput
        payload = json.loads(msg.payload.decode())
        current_throughput = float(payload["throughput"])
        print(
            f"----------------> CURRENT THROUGHPUT: {current_throughput * int(1e3)} Mbps"
        )

    natsclient.subscribe(subject="communications.state", callback=callback)
    natsclient.subscribe(subject="communications.throughput", callback=updateThroughput)

    for episode in range(n_trajectories):
        print("Episode: " + str(episode))

        # Save the actual time to compute the runtime at the end of the episode
        initial_time = time.time()

        isFinished = False

        # Read paths
        path_list = []

        with open(
            os.path.join(trajectories_files, "path" + str(episode) + ".csv")
        ) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            csv_reader.__next__()
            for row in csv_reader:
                path_list.append([float(row[0]), float(row[1]), float(row[2])])

        # Delay between episodes to avoid crashs
        time.sleep(1)

        caviar_tools.addPedestriansOnPath(
            client, os.path.join(trajectories_files, "path" + str(episode) + ".csv")
        )

        # Reset the AirSim simulation
        caviar_tools.airsim_reset(client)

        caviar_tools.airsim_setpose(
            client,
            caviar_config.drone_ids[0],
            float(path_list[0][0]),
            float(path_list[0][1]),
            float(path_list[0][2]),
            0,
            0,
            0,
            0,
        )
        time.sleep(0.5)

        initial_timestamp = caviar_tools.airsim_gettimestamp(
            client, caviar_config.drone_ids[0]
        )

        # Takeoff and start the UAV trajectory
        caviar_tools.airsim_takeoff_all(client)
        time.sleep(1)
        caviar_tools.move_to_point(
            client,
            caviar_config.drone_ids[0],
            float(path_list[0][0]),
            float(path_list[0][1]),
            float(path_list[0][2]),
            10,
        )

        actualWaypoint = 0

        # Pause the simulation
        client.simPause(True)
        while not (isFinished):
            # Continue the simulation for a time defined in "simulation_time_step"
            start_time = time.time()

            if is_sync:
                if sionna_finished_running:
                    client.simContinueForTime(simulation_time_step)
                    sionna_finished_running = False
            else:
                client.simContinueForTime(simulation_time_step)
                # client.simPause(False)
            natsclient.wait(count=2)

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
                img = cv2.imdecode(
                    airsim.string_to_uint8_array(rawimg), cv2.IMREAD_COLOR
                )

                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                img = addNoise(img, current_throughput)

                img = Image.fromarray(img_rgb)
                image, bbox, rev_tensor = transform(img)
                image = image.to(device)[None]
                rev_tensor = rev_tensor.to(device)[None]

                with torch.no_grad():
                    model.eval()
                    raw_results = model(image)
                    results = post_proccess(raw_results, rev_tensor)

                    output_image = draw_bboxes(
                        image, results, idx2label=cfg.dataset.class_list
                    )

                    output_image.save("./output/with_bounding_box.png")

                    try:
                        pred_class = cfg.dataset.class_list[
                            int(results[0][0].cpu().numpy()[0])
                        ]
                        pred_prob = results[0][0].cpu().numpy()[5]
                    except:
                        pred_class = None
                        pred_prob = None
                try:
                    target_is_detected = pred_class == "Person" and pred_prob >= 0.9
                    if target_is_detected:
                        print(f"> Detected class: {pred_class}")
                        print(f"> Human detected probability: {pred_prob}")
                        rescue_time = get_time_for_rescue(current_throughput * 1e9)
                        throughputs_during_rescue.append(current_throughput)
                        times_waited_during_rescue.append(rescue_time)
                        rescue_state = client.simDestroyObject(
                            caviar_config.pedestrians[actualWaypoint - 1]
                        )
                        if rescue_state == False:
                            client.simDestroyObject(
                                caviar_config.pedestrians[actualWaypoint]
                            )
                        print(f"> Rescue will take: {rescue_time} sec.")
                        rescued_targets = rescued_targets + 1
                        simu_time_of_rescue.append(
                            (airsim_timestamp - initial_timestamp) * 1e-9
                        )
                        simu_pose_of_rescue.append(
                            convertPositionFromAirSimToSionna(
                                uav_pose[0], uav_pose[1], uav_pose[2]
                            )
                        )
                        if is_rescue_mission:
                            person_to_be_rescued = True
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
                    + str((airsim_timestamp) * 1e-9).encode()
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
                # Check if is reaching or already reached a waypoint
                if (
                    caviar_tools.has_uav_arrived(
                        client,
                        uav,
                        path_list[actualWaypoint][0],
                        path_list[actualWaypoint][1],
                        path_list[actualWaypoint][2],
                    )
                    or reached_waypoint
                ):
                    reached_waypoint = True
                    if rescue_steps == 0:
                        # Must start rescue
                        if person_to_be_rescued:
                            print("Rescue")
                            rescue_steps_raw = rescue_time / simulation_time_step
                            if rescue_time % simulation_time_step == 0:
                                rescue_steps = int(rescue_steps_raw)
                            else:
                                rescue_steps = int(rescue_steps_raw) + 1
                        # No one to rescue. Must go to the next waypoint
                        else:
                            actualWaypoint = actualWaypoint + 1
                            caviar_tools.move_to_point(
                                client,
                                uav,
                                path_list[actualWaypoint][0],
                                path_list[actualWaypoint][1],
                                path_list[actualWaypoint][2],
                            )

                            reached_waypoint = False

                            print(actualWaypoint)

                            if actualWaypoint == (len(path_list) - 4):
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
                    # Continues the rescue
                    else:
                        rescue_steps = rescue_steps - 1
                        if rescue_steps == 0:
                            person_to_be_rescued = False  # finished rescue

            output_folder = os.path.join(os.getcwd(), "runs")
            if save_multimodal:
                caviar_tools.airsim_save_external_images(
                    client, output_folder, "FixedCamera1"
                )

            end_time = time.time()
            print(f"CAVIAR in-loop step duration (seconds): {end_time-start_time}")
            print(
                f"> Simulation duration (seconds): {(airsim_timestamp-initial_timestamp)*1e-9}"
            )

        print(f"Total mission time: {(airsim_timestamp-initial_timestamp)*1e-9}")
        print(f"Rescued targets: {rescued_targets}")
        np.savez(
            "mission_log.npz",
            total_mission_time=(airsim_timestamp - initial_timestamp) * 1e-9,
            rescued_targets=rescued_targets,
            simu_time_of_rescue=simu_time_of_rescue,
            simu_pose_of_rescue=simu_pose_of_rescue,
            throughputs_during_rescue=throughputs_during_rescue,
            times_waited_during_rescue=times_waited_during_rescue,
        )
