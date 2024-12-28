import numpy as np
from scipy.constants import Boltzmann  # 1.380649e-23 J.K^-1


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
    noise_power_dBW = Watts2dBW(noise_PSD * bandwidth) + noise_figure
    noise_power_Watts = dBW2Watts(noise_power_dBW)
    ############################## Interference calculation ###################
    interference_power_dBW = -120
    interference_power_Watts = dBW2Watts(interference_power_dBW)
    ###########################################################################
    tx_power_watts = 0.25  # 250 milliwatts
    SINR = ((equivalentChannelMagnitude.A1**2) * tx_power_watts) / (
        noise_power_Watts + interference_power_Watts
    )  # A1 used to flatten
    spectral_efficiency = np.log2(1 + SINR)
    bit_rate = (bandwidth * spectral_efficiency).reshape(H_shape[0], H_shape[1])
    return bit_rate
