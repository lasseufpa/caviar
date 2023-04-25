'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script to generate datasets from UE4/AirSim simulations
V1.0
'''

import caviar_config
import caviar_tools
import csv
import time
import os
from subprocess import call
import zmq
import cv2
import airsim


# Number of trajectories to be executed
# Each trajectory is an episode
n_trajectories = 500
ns3_path = '/home/fhb/5glena/ns-3-dev'

# Creat a folder to write the UE4 simulation result
try:
    os.mkdir('./episodes')
except OSError as error:
    print(error)

try:
    os.mkdir('./5glena_output')
except OSError as error:
    print(error)

client = caviar_tools.airsim_connect()

#  Socket to talk to server
context = zmq.Context()

print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

for episode in range(n_trajectories):
    print('Episode: ' + str(episode))

    # Save the actual time to compute the run-time at the end of the episode
    initial_time = time.time()

    landed = False
    takeoff_complete = False

    # Delay between episodes to avoid crashs
    time.sleep(1)

    # Reset the airsim simulation
    caviar_tools.airsim_reset(client)

    # takeoff and start the UAV trajectory
    caviar_tools.airsim_takeoff_all(client)
    caviar_tools.move_on_path(client, caviar_config.drone_ids[0], './waypoints/trajectories/path' + str(episode ) + '.csv')

    with open('./episodes/ep' + str(episode) +  '.csv', mode='w', newline='') as csv_file:

        # CSV header
        fieldnames = ["timestamp", "obj", "pos_x", "pos_y", "pos_z", "orien_x", "orien_y", "orien_z", "orien_w", "linear_acc_x", "linear_acc_y", "linear_acc_z", "linear_vel_x", "linear_vel_y", "linear_vel_z", "angular_acc_x", "angular_acc_y", "angular_acc_z", "angular_vel_x", "angular_vel_y", "angular_vel_z"]

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Pause the simulation
        client.simPause(True)

        while not(landed):
            #Continue the simulation for 10ms
            client.simContinueForTime(0.10)

            # Get an write information about each UAV in the configuration file (caviar_config.py)
            for uav in caviar_config.drone_ids:
                uav_pose = caviar_tools.airsim_getpose_offset(client, uav)
                uav_orien = caviar_tools.airsim_getorientation(client, uav)
                uav_linear_acc = caviar_tools.airsim_getlinearacc(client, uav)
                uav_linear_vel = caviar_tools.airsim_getlinearvel(client, uav)
                uav_angular_acc = caviar_tools.airsim_getangularacc(client, uav)
                uav_angular_vel = caviar_tools.airsim_getangularvel(client, uav)
                airsim_timestamp = caviar_tools.airsim_gettimestamp(client, uav)

                # Get frames
                rawimg = caviar_tools.airsim_getimages(client, caviar_config.drone_ids[0])
                #img = cv2.imdecode(airsim.string_to_uint8_array(rawimg), cv2.IMREAD_COLOR)
                #height, width, depth = img.shape
                #img_size_bits = height * width * depth * 8 # Considering that each channel from a RGB image is represented by 8 bits color depth (0, 255)
                #img_size_bytes = img_size_bits/1024
                #cv2.imshow("window_name", img)
                #print('img_size_bytes: ', img_size_bytes)

                writer.writerow({"timestamp": airsim_timestamp, "obj": uav, "pos_x": uav_pose[0], "pos_y": uav_pose[1], "pos_z": uav_pose[2], "orien_w": uav_orien[3], "orien_x": uav_orien[0], "orien_y": uav_orien[1], "orien_z": uav_orien[2], "linear_acc_x": uav_linear_acc[0], "linear_acc_y": uav_linear_acc[1],"linear_acc_z": uav_linear_acc[2], "linear_vel_x": uav_linear_vel[0], "linear_vel_y": uav_linear_vel[1],"linear_vel_z": uav_linear_vel[2], "angular_acc_x": uav_angular_acc[0], "angular_acc_y": uav_angular_acc[1],"angular_acc_z": uav_angular_acc[2], "angular_vel_x": uav_angular_vel[0], "angular_vel_y": uav_angular_vel[1], "angular_vel_z": uav_angular_vel[2]})

                #Call NS-3 5G-Lena simulation

                #call(["./waf", "--run", "cttc-realistic-beamforming", "'--command=%s --deltaX=" + str(uav_pose[0]) + " --deltaY=" + str(uav_pose[1]) + " --algType=Real --rngRun=1 --numerology=0 --gnbAntenna=3gpp --ueAntenna=3gpp --uePower=10 --scenario=Uma --simTag=-sim-campaign-algReal-rng1-mu0-gNb3gpp-ue3gpp --resultsDir=/home/fhb/git/ITU-Challenge-ML5G-PHY-RL/5glena_output/ --dbName=realistic_beamforming" + str(episode) + str(airsim_timestamp) + ".db --tableName=results'"], cwd=ns3_path)

                print("Sending request %s …" % episode)
                # socket.send(str(uav_pose[0]) + "-" + str(uav_pose[1]) + "-" + str(uav_pose[2]))
                socket.send_string(str(uav_pose[0]) + "/" + str(uav_pose[1]) + "/" + str(uav_pose[2]) + "/" + str(0))
                # socket.send_string(str(uav_pose[0]) + str(uav_pose[1]) + str(uav_pose[2]))
                #  Get the reply.
                message = socket.recv()
                print("Received reply %s [ %s ]" % (episode, message))


                # Check if the UAV is landed or has collided and finish the episode
                if takeoff_complete:
                    if (uav_pose[2] >= 7.5):
                        print('Episode ' + str(episode) + ' concluded with ' + str(time.time() - initial_time) + 's')
                        client.simPause(False)
                        landed = True
                else:
                    if (uav_pose[2] <= -5):
                        takeoff_complete = True
                if (caviar_tools.airsim_getcollision(client, uav)):
                    client.simPause(False)
                    landed = True

            # Get an write information about others objects in the simulation (cars and pedestrians). Each object is described in the configuration file (caviar_config.py)
            for obj in caviar_config.ue_objects:
                object_pose = caviar_tools.unreal_getpose(client, obj)
                object_orien = caviar_tools.unreal_getorientation(client, obj)

                writer.writerow({"timestamp": airsim_timestamp, "obj": obj, "pos_x": object_pose[0], "pos_y": object_pose[1], "pos_z": object_pose[2], "orien_w": object_orien[3], "orien_x": object_orien[0], "orien_y": object_orien[1], "orien_z": object_orien[2], "linear_acc_x": "", "linear_acc_y": "","linear_acc_z": "", "linear_vel_x": "", "linear_vel_y": "","linear_vel_z": "", "angular_acc_x": "", "angular_acc_y": "","angular_acc_z": "", "angular_vel_x": "", "angular_vel_y": "", "angular_vel_z": ""})
