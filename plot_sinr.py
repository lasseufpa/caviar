import numpy as np
import os

current_dir = os.getcwd()
output_filename = os.path.join(current_dir, "allruns4.npz")
mission_log = np.load(output_filename, allow_pickle=True)
oracle_bit_rate_Gbps = mission_log["best_bit_rate_Gbps"]
random_bit_rate_Gbps = mission_log["random_bit_rate_Gbps"]

oracle_bit_rate_bps = oracle_bit_rate_Gbps * 1e9
random_bit_rate_bps = random_bit_rate_Gbps * 1e9

bandwidth = 40e6

best_sinr_linear = np.float_power(2, (oracle_bit_rate_bps/bandwidth)) - 1 # mW
random_sinr_linear = np.float_power(2, (random_bit_rate_bps/bandwidth)) - 1 # mW

best_sinr_dBm = 10 * np.log10(best_sinr_linear) # dBm
random_sinr_dBm = 10 * np.log10(random_sinr_linear) # dBm

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

plt.plot(range(len(oracle_bit_rate_Gbps)), best_sinr_dBm, label="Oracle")
plt.plot(range(len(oracle_bit_rate_Gbps)), random_sinr_dBm, label="Random")
plt.grid(True)
plt.legend()
plt.xlabel("Step")
plt.ylabel("SINR (dBm)")
plt.savefig("sinr_dBm.png")