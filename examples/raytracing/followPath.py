import os
import airsim
import time
import obj_move


def executeOneStep(step):
    time.sleep(5)
    airsim_client.simPause(True)
    uav_pose = airsim_client.simGetVehiclePose()
    obj_move.moveTo(current_position_path, step, new_x=uav_pose.position.x_val)
    airsim_client.simPause(False)


current_position_path = os.path.join(
    "C:",
    "Users",
    "takashi",
    "Desktop",
    "CAVIAR_test",
    "simulation",
    "base",
    "Simple_car.object",
)


airsim_client = airsim.MultirotorClient()
airsim_client.confirmConnection()
airsim_client.enableApiControl(True)
airsim_client.armDisarm(True)

# Execute takeoff
airsim_client.moveToPositionAsync(0, 0, -50, 10).join()

# Move to the end of the road
airsim_client.moveToPositionAsync(-700, 0, -50, 10)

for step in range(3):
    executeOneStep(step)
