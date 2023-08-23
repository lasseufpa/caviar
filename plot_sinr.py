import numpy as np
import os

def dBW2Watts(dBW):
    return np.float_power(10, (dBW / 10))


def Watts2dBW(Watts):
    return 10*np.log10(Watts)


from scipy.constants import Boltzmann  # 1.380649e-23 J.K^-1
bandwidth=40e6
############################## Noise calculation ###########################
standard_noise_temperature = 290  # Standard value is T_o = 290 Kelvin = ~16.85 °C
device_noise_temperature = 298.15  # The adopted value can be T_e = 25 °C = 298.15 K
noise_factor = 1 + (device_noise_temperature / standard_noise_temperature)
noise_figure = 10 * np.log10(noise_factor)  # in dB
noise_PSD = Boltzmann * standard_noise_temperature # in Joules, which is equal to W/Hz
noise_power_dBW = Watts2dBW(noise_PSD * bandwidth) + noise_figure # noise_figure = around 100 dBW
noise_power_Watts = dBW2Watts(noise_power_dBW)
noise_power_mW = noise_power_Watts * 1e3
############################## Interference calculation ###################
interference_power_dBW = 100
interference_power_Watts = dBW2Watts(interference_power_dBW)
interference_power_mW = interference_power_Watts * 1e3
#############################################################################

current_dir = os.getcwd()
output_filename = os.path.join(current_dir, "allruns_v3.npz")
mission_log = np.load(output_filename, allow_pickle=True)
oracle_bit_rate_Gbps = mission_log["best_bit_rate_Gbps"]
random_bit_rate_Gbps = mission_log["random_bit_rate_Gbps"]

oracle_bit_rate_bps = oracle_bit_rate_Gbps * 1e9
random_bit_rate_bps = random_bit_rate_Gbps * 1e9

bandwidth = 40e6

best_snr_linear = np.float_power(2, (oracle_bit_rate_bps/bandwidth)) - 1
random_snr_linear = np.float_power(2, (random_bit_rate_bps/bandwidth)) - 1

best_signal_power_mW = best_snr_linear*noise_power_mW
random_signal_power_mW = random_snr_linear*noise_power_mW


best_sinr_linear = best_signal_power_mW/(noise_power_mW*interference_power_mW)
random_sinr_linear = random_signal_power_mW/(noise_power_mW*interference_power_mW)


best_snr_dB = 10 * np.log10(best_snr_linear) # dB
random_snr_dB = 10 * np.log10(random_snr_linear) # dB

best_sinr_linear_dB = 10 * np.log10(best_sinr_linear)
random_sinr_linear_dB = 10 * np.log10(random_sinr_linear)

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

# plt.scatter(range(len(oracle_bit_rate_Gbps)), best_snr_dB, label="Oracle")
# plt.scatter(range(len(oracle_bit_rate_Gbps)), random_snr_dB, label="Random", marker='.')
# plt.grid(True)
# plt.legend()
# plt.xlabel("Step")
# plt.ylabel("SNR (dB)")
# plt.savefig("snr_dB.png")

plt.scatter(range(len(oracle_bit_rate_Gbps)), best_sinr_linear_dB, label="Oracle")
plt.scatter(range(len(oracle_bit_rate_Gbps)), random_sinr_linear_dB, label="Random", marker='.')
plt.grid(True)
plt.legend()
plt.yticks(np.arange(-90, 21, 10))
plt.xlabel("Step")
plt.ylabel("SINR (dB)")
plt.savefig("sinr_dB.png")

# plt.scatter(range(len(oracle_bit_rate_Gbps)), best_signal_power_mW, label="Oracle")
# plt.scatter(range(len(oracle_bit_rate_Gbps)), random_signal_power_mW, label="Random", marker='.')
# plt.grid(True)
# plt.legend()
# plt.xlabel("Step")
# plt.ylabel("Signal power (mW)")
# plt.savefig("Signal power_mW.png")