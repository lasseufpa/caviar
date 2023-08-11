import numpy as np


MAX_TIME = 180  # 3 minutes to complete the game
# MIN_TIME =  # Here, we need the minimum time
NUMBER_OF_WP = 10

def getBitRate(equivalentChannelMagnitude, bandwidth = 40e6):
    '''
    Calculates the bit rate for all the possible beam pair combinations.
    '''
    H_shape = equivalentChannelMagnitude.shape
    No_PSD = -174 # -174 dBm/Hz is the usual PSD value for thermal noise
    noise_power_mW = np.float_power(10, (No_PSD/10)) * bandwidth # linear scale
    SINR = (equivalentChannelMagnitude.A1**2)/noise_power_mW # A1 is used to flatten the matrix
    spectral_efficiency = np.log2(1 + SINR)
    bit_rate = (bandwidth * spectral_efficiency).reshape(H_shape[0],H_shape[1])
    return bit_rate


def get_time_for_wp(equivalentChannelMagnitude, const):
    '''
    Using 10 Pictures rule:
    2.076.727 bytes (4K image) x 10 x 8 = 160.613.816 bits to transmit
    We can calculate the time for transmit all
    '''
    tx_max = 2076727 * 10 * 8
    bit_rate = getBitRate(equivalentChannelMagnitude, const)
    time_to_tx = (tx_max / bit_rate)
    return time_to_tx


def lost_for_time(time, score):
    if (time > MAX_TIME ):
        score = score - 2400
        return score, True
    else:
        return score


def person_score(person):
    if (person):
        return 1


def get_person_score(n_people):
    return 600*n_people


#def get_time_parked(caviar_stopped):
#    init = time.time()
#    # CAVIAR IN LOOP - BEAM SELECT
#    stopped = time.time()
#    return stopped - init

def get_wp_score(equivalentChannelMagnitude, const, score=0,time=0,persons=0):
    wp_time = get_time_for_wp(equivalentChannelMagnitude,const)
    persons += person_score(True)
    score = get_person_score(persons)
    score, lost = lost_for_time(time,score) # Here, you need to inl
    if(lost):
        return score, lost
    return wp_time, score, lost, persons


# if __name__=='__main_':
    