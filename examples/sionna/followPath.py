import time
import airsim
from execute_run import run
from pynats import NATSClient
import json

total_ues = 1 # + len(caviar_config.ue_objects)


# def executeOneStep(current_step):
#     """Executes step on Sionna according to the current position in AirSim.

#     Args:
#         current_step (int): The current step index
#     """
#     time.sleep(8)
#     airsim_client.simPause(True)
#     uav_pose = airsim_client.simGetVehiclePose()
#     run(
#         current_step,
#         new_x=uav_pose.position.x_val,
#         new_y=uav_pose.position.y_val,
#         new_z=uav_pose.position.z_val,
#     )
#     airsim_client.simPause(False)


# airsim_client = airsim.MultirotorClient()
# airsim_client.confirmConnection()
# airsim_client.enableApiControl(True)
# airsim_client.armDisarm(True)

# # Execute takeoff
# airsim_client.moveToPositionAsync(0, 0, -50, 10).join()

# # Move to the end of the road on Unreal
# airsim_client.moveToPositionAsync(100, 70, -50, 10)

# for current_step in range(3):
#     executeOneStep(current_step)

with NATSClient() as natsclient:

    natsclient.connect()

    def executeOneStep(msg):
        """Executes step on Sionna according to the current position in AirSim.

        Args:
            current_step (int): The current step index
        """
        # print(msg.payload)
        payload = json.loads(msg.payload.decode())
        # print(f"payload['position']['x']: {payload['position']['x']}")
        # print(f"payload['position']['y']: {payload['position']['y']}")
        # print(f"payload['position']['z']: {payload['position']['z']}")
        run(
            current_step,
            new_x=payload['position']['x'],
            new_y=payload['position']['y'],
            new_z=payload['position']['z'],
        )
        natsclient.wait(count=total_ues)

    natsclient.subscribe(subject="caviar.ue.mobility.positions", callback=executeOneStep)

    natsclient.wait(count=total_ues)