import numpy as np
import os

current_dir = os.getcwd()
output_filename = os.path.join(current_dir, "mission_log.npz")
mission_log = np.load(output_filename, allow_pickle=True)


total_mission_time=mission_log["total_mission_time"]
rescued_targets=mission_log["rescued_targets"]
simu_time_of_rescue=mission_log["simu_time_of_rescue"]
throughputs_during_rescue=mission_log["throughputs_during_rescue"]
times_waited_during_rescue=mission_log["times_waited_during_rescue"]

print(f'\n##################### MISSION LOG ###################\n')
print(f'total_mission_time: {total_mission_time}')
print(f'rescued_targets: {rescued_targets}')
print(f'simu_time_of_rescue: {simu_time_of_rescue}')
print(f'throughputs_during_rescue: {throughputs_during_rescue}')
print(f'times_waited_during_rescue: {times_waited_during_rescue}\n')