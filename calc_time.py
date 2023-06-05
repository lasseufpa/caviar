import time
import numpy as np


MAX_TIME = 180  # 3 minutes to complete the game
MIN_TIME =  # Here, we need the minimum time
NUMBER_OF_WP = 10



# CAVIAR function
def Bit_rate(H, const = 440.35, bandwidth = 40e6):
    SINR = const * (H**2)
    se = np.log2(1 + SINR)
    R = float(bandwidth * se)
    return R


def get_time_for_wp(H, const):  
    '''
    Using 10 Picutes rule:
    2.076.727 bytes (4K image) x 10 x 8 = 160.613.816 bits to transmit
    We can calculate the time for transmit all
    '''
    tx_max = 2076727 * 10 * 8
    bit_rate = Bit_rate(H, const)
    time_to_tx = (tx_max / bit_rate)
    return time_to_tx


def lost_for_time(time, score):
    if (time > MAX_TIME):
        score = score - 2400
        return score, True
    else:
        return score
    
    
def person_score(person):
    if (person):
        return 1
    
def get_person_score(n_people):
    return 600*n_people
     
def get_time_sum(waytime):
    return np.sum(waytime)
    
#def get_time_parked(caviar_stopped):
#    init = time.time()
#    # CAVIAR IN LOOP - BEAM SELECT
#    stopped = time.time()
#    return stopped - init

def get_wp_score(score,time,H,const):
    score, lost = lost_for_time(time,score)
    if(lost):
        return score
    wp_time = get_time_for_wp(np.abs(H),const)
    

if __name__=='__main__':
    waytime = np.zeros(NUMBER_OF_WP)
    