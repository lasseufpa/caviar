import numpy as np


MAX_TIME = 180  # 3 minutes to complete the game
MIN_TIME =  # Here, we need the minimum time
NUMBER_OF_WP = 10

# CAVIAR function
def Bit_rate(H_mag, const = 440.35, bandwidth = 40e9):
    SINR = const * (H_mag**2)
    se = np.log2(1 + SINR)
    R = float(bandwidth * se)
    return R


def get_time_for_wp(H_mag, const):  
    '''
    Using 10 Pictures rule:
    2.076.727 bytes (4K image) x 10 x 8 = 160.613.816 bits to transmit
    We can calculate the time for transmit all
    '''
    tx_max = 2076727 * 10 * 8
    bit_rate = Bit_rate(H_mag, const)
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

def get_wp_score(score=0,time=0,H_mag,const,persons=0):
    wp_time = get_time_for_wp(H_mag,const)
    persons += person_score(True)
    score = get_person_score(persons)
    score, lost = lost_for_time(time,score) # Here, you need to inl
    if(lost):
        return score, lost
    return wp_time, score, lost, persons
if __name__=='__main_':
    