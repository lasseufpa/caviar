import numpy as np
import os

# dataset_name = "runs20241216_normalized"
dataset_name = "runs20241216_not_normalized"
calc_SINR = True
interference_power_dBW = -120  # also -90 dBm
tx_power_watts = 0.25  # 250 milliwatts

# dataset_name = "allruns_v7"
# calc_SINR = True
# interference_power_dBW = 100


def dBW2Watts(dBW):
    return np.float_power(10, (dBW / 10))


def Watts2dBW(Watts):
    return 10 * np.log10(Watts)


def getBitRate(equivalentChannelMagnitude, bandwidth=40e6):
    """
    Calculates the bit rate for all the possible beam pair combinations.
    """
    H_shape = equivalentChannelMagnitude.shape
    ############################## Noise calculation ###########################
    standard_noise_temperature = 290  # Standard value is T_o = 290 Kelvin = ~16.85 °C
    device_noise_temperature = 298.15  # The adopted value can be T_e = 25 °C = 298.15 K
    noise_factor = 1 + (device_noise_temperature / standard_noise_temperature)
    noise_figure = 10 * np.log10(noise_factor)  # in dB
    noise_PSD = (
        Boltzmann * standard_noise_temperature
    )  # in Joules, which is equal to W/Hz
    noise_power_dBW = Watts2dBW(noise_PSD * bandwidth) + noise_figure  # -124.88 dBW
    noise_power_dBW_AK = -170
    noise_power_Watts = dBW2Watts(noise_power_dBW)
    ############################## Interference calculation ###################
    interference_power_Watts = dBW2Watts(interference_power_dBW)
    ###########################################################################
    # SNR = (equivalentChannelMagnitude.A1**2) / (
    #     noise_power_mW + interference_power_mW
    # )  # A1 used to flatten
    SNR = np.array(
        ((equivalentChannelMagnitude.flatten() ** 2) * tx_power_watts)
        / (noise_power_Watts)
    )
    SINR = np.array(
        ((equivalentChannelMagnitude.flatten() ** 2) * tx_power_watts)
        / (noise_power_Watts + interference_power_Watts)
    )

    if calc_SINR:
        spectral_efficiency = np.log2(1 + SINR)
    else:
        spectral_efficiency = np.log2(1 + SNR)

    bit_rate = (bandwidth * spectral_efficiency).reshape(H_shape[0], H_shape[1])
    return bit_rate


from scipy.constants import Boltzmann  # 1.380649e-23 J.K^-1

current_dir = os.getcwd()
output_filename = os.path.join(current_dir, dataset_name + ".npz")
mission_log = np.load(output_filename, allow_pickle=True)
equivalentChannelMagnitudes = mission_log["equivalentChannelMagnitude"]
bandwidth = 40e6

oracle_SNRs = []
random_SNRs = []
for H in equivalentChannelMagnitudes:
    best_ray = np.argwhere(H == np.max(H))
    SNR = getBitRate(equivalentChannelMagnitude=H, bandwidth=bandwidth)
    oracle_SNRs.append(SNR[best_ray[0][0], best_ray[0][1]])
    random_SNRs.append(SNR[np.random.randint(0, 4), np.random.randint(0, 64)])

print(f"mean bps: {np.mean(oracle_SNRs)}")
print(f"variance bps: {np.var(oracle_SNRs)}")

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

plt.scatter(range(len(oracle_SNRs)), oracle_SNRs, label="Oracle")
plt.scatter(range(len(random_SNRs)), random_SNRs, label="Random", marker=".")
plt.grid(True)
plt.legend()
# plt.yticks(np.arange(-90, 21, 10))
plt.xlabel("Step")
if calc_SINR:
    plt.ylabel("rate (bps)")
    plt.savefig("rate_" + str(interference_power_dBW) + "dB_" + dataset_name + ".png")
else:
    plt.ylabel("rate (bps)")
    plt.savefig("rate_snr_" + dataset_name + ".png")
