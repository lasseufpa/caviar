import numpy as np
import os

current_dir = os.getcwd()

mission_log_names = ["oracle", "oracle2", "decTree", "random"]

for name in mission_log_names:
    output_filename = os.path.join(current_dir, f"{name}_mission_log.npz")
    mission_log = np.load(output_filename, allow_pickle=True)
    total_mission_time=mission_log["total_mission_time"]
    rescued_targets=mission_log["rescued_targets"]
    simu_pose_of_rescue=mission_log["simu_pose_of_rescue"]
    simu_time_of_rescue=mission_log["simu_time_of_rescue"]
    throughputs_during_rescue=mission_log["throughputs_during_rescue"]
    times_waited_during_rescue=mission_log["times_waited_during_rescue"]

    print(f'\n##################### MISSION LOG: {name} ###################\n')
    print(f'total_mission_time: {total_mission_time} seconds')
    print(f'rescued_targets: {rescued_targets} people')
    print(f'simu_pose_of_rescue: \n{simu_pose_of_rescue} coordinates')
    print(f'simu_time_of_rescue: {simu_time_of_rescue} seconds')
    print(f'throughputs_during_rescue: {throughputs_during_rescue} Gbps')
    print(f'times_waited_during_rescue: {times_waited_during_rescue} seconds\n')