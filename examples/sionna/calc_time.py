import numpy as np
from scipy.constants import Boltzmann  # 1.380649e-23 J.K^-1


MAX_TIME = 180  # 3 minutes to complete the game
# MIN_TIME =  # Here, we need the minimum time
NUMBER_OF_WP = 10


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
    noise_power_dBW = (
        Watts2dBW(noise_PSD * bandwidth) + noise_figure
    )  # noise_figure = around 100 dBW
    noise_power_Watts = dBW2Watts(noise_power_dBW)
    noise_power_mW = noise_power_Watts * 1e3
    ############################## Interference calculation ###################
    interference_power_dBW = 100
    interference_power_Watts = dBW2Watts(interference_power_dBW)
    interference_power_mW = interference_power_Watts * 1e3
    ###########################################################################
    SNR = (equivalentChannelMagnitude.A1**2) / (
        noise_power_mW + interference_power_mW
    )  # A1 used to flatten
    spectral_efficiency = np.log2(1 + SNR)
    bit_rate = (bandwidth * spectral_efficiency).reshape(H_shape[0], H_shape[1])
    return bit_rate


def get_time_for_wp(equivalentChannelMagnitude, const):
    """
    Using 10 Pictures rule:
    2.076.727 bytes (4K image) x 10 x 8 = 160.613.816 bits to transmit
    We can calculate the time for transmit all
    """
    tx_max = 2076727 * 10 * 8
    bit_rate = getBitRate(equivalentChannelMagnitude, const)
    time_to_tx = tx_max / bit_rate
    return time_to_tx


def lost_for_time(time, score):
    if time > MAX_TIME:
        score = score - 2400
        return score, True
    else:
        return score


def person_score(person):
    if person:
        return 1


def get_person_score(n_people):
    return 600 * n_people


# def get_time_parked(caviar_stopped):
#    init = time.time()
#    # CAVIAR IN LOOP - BEAM SELECT
#    stopped = time.time()
#    return stopped - init


def get_wp_score(equivalentChannelMagnitude, const, score=0, time=0, persons=0):
    wp_time = get_time_for_wp(equivalentChannelMagnitude, const)
    persons += person_score(True)
    score = get_person_score(persons)
    score, lost = lost_for_time(time, score)  # Here, you need to inl
    if lost:
        return score, lost
    return wp_time, score, lost, persons


# if __name__=='__main_':
