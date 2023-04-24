import time
import airsim
from execute_run import run


def executeOneStep(current_step):
    """Executes step on Sionna according to the current position in AirSim.

    Args:
        current_step (int): The current step index
    """
    time.sleep(8)
    airsim_client.simPause(True)
    uav_pose = airsim_client.simGetVehiclePose()
    run(
        current_step,
        new_x=uav_pose.position.x_val,
        new_y=uav_pose.position.y_val,
        new_z=uav_pose.position.z_val,
    )
    airsim_client.simPause(False)


airsim_client = airsim.MultirotorClient()
airsim_client.confirmConnection()
airsim_client.enableApiControl(True)
airsim_client.armDisarm(True)

# Execute takeoff
airsim_client.moveToPositionAsync(0, 0, -50, 10).join()

# Move to the end of the road on Unreal
airsim_client.moveToPositionAsync(100, 70, -50, 10)

# for current_step in range(3):
#     executeOneStep(current_step)
