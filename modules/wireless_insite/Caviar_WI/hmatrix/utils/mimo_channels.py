import os
import datetime

import numpy as np
import math
from .p2mpaths import P2mPaths
from .p2mcir import P2mCir


def arrayFactorGivenAngleForULA(numAntennaElements, theta, normalizedAntDistance=0.5, angleWithArrayNormal=0):

    indices = np.arange(numAntennaElements)
    if (angleWithArrayNormal == 1):
        arrayFactor = np.exp(-1j * 2 * np.pi * normalizedAntDistance * indices * np.sin(theta))
    else:  # default
        arrayFactor = np.exp(-1j * 2 * np.pi * normalizedAntDistance * indices * np.cos(theta))
    return arrayFactor / np.sqrt(numAntennaElements)  # normalize to have unitary norm

def getNarrowBandULAMIMOChannel(azimuths_tx, azimuths_rx, p_gainsdB, number_Tx_antennas, number_Rx_antennas,
                                normalizedAntDistance=0.5, angleWithArrayNormal=0, pathPhases=None):
    
    azimuths_tx = np.deg2rad(azimuths_tx)
    azimuths_rx = np.deg2rad(azimuths_rx)
    # nt = number_Rx_antennas * number_Tx_antennas #np.power(antenna_number, 2)
    m = np.shape(azimuths_tx)[0]  # number of rays
    H = np.matrix(np.zeros((number_Rx_antennas, number_Tx_antennas)))

    gain_dB = p_gainsdB
    path_gain = np.power(10, gain_dB / 10)
    path_gain = np.sqrt(path_gain)

    #generate uniformly distributed random phase in radians
    if pathPhases is None:
        pathPhases = 2*np.pi * np.random.rand(len(path_gain))
    else:
        #convert from degrees to radians
        pathPhases = np.deg2rad(pathPhases)

    #include phase information, converting gains in complex-values
    path_complexGains = path_gain * np.exp(1j * pathPhases)

    # recall that in the narrowband case, the time-domain H is the same as the
    # frequency-domain H
    for i in range(m):
        at = np.matrix(arrayFactorGivenAngleForULA(number_Tx_antennas, azimuths_tx[i], normalizedAntDistance,
                                                   angleWithArrayNormal))
        ar = np.matrix(arrayFactorGivenAngleForULA(number_Rx_antennas, azimuths_rx[i], normalizedAntDistance,
                                                   angleWithArrayNormal))
        H = H + path_complexGains[i] * ar.conj().T * at  # outer product of ar Hermitian and at
        #H = H + path_complexGains[i] * ar
    # factor = (np.linalg.norm(path_complexGains) / np.sum(path_complexGains)) * np.sqrt(
    #     number_Rx_antennas * number_Tx_antennas)  # scale channel matrix
    # H *= factor  # normalize for compatibility with Anum's Matlab code

    return H

def watts_to_dbm(power_watts):
    dbm = 10 * math.log10(power_watts * 1000)
    return dbm

def dbm_to_watts(dbm):
    return 10 ** (dbm / 10)

def degrees_to_radians(degrees):
    return np.radians(degrees)

def dft_codebook(dim):
    seq = np.matrix(np.arange(dim))
    mat = seq.conj().T * seq
    w = np.exp(-1j * 2 * np.pi * mat / dim)
    return w

def getDFTOperatedChannel(H, number_Tx_antennas, number_Rx_antennas):
    wt = dft_codebook(number_Tx_antennas)   #precoding
    wr = dft_codebook(number_Rx_antennas)   #combining
    dictionaryOperatedChannel = wr.conj().T * H * wt
    # dictionaryOperatedChannel2 = wr.T * H * wt.conj()
    return dictionaryOperatedChannel  # return equivalent channel after precoding and combining


'''def deep_mimo_array_response(Dod, DoA, M_TX, M_RX, fc, c=3e8):
     # TX Array Response - BS
    gamma_TX = 1j * kd_TX * np.array([np.sin(np.radians(DoD_theta)) * np.cos(np.radians(DoD_phi)),
                                      np.sin(np.radians(DoD_theta)) * np.sin(np.radians(DoD_phi)),
                                      np.cos(np.radians(DoD_theta))])
    array_response_TX = np.exp(M_TX_ind @ gamma_TX)

    # RX Array Response - UE or BS
    gamma_RX = 1j * kd_RX * np.array([np.sin(np.radians(DoA_theta)) * np.cos(np.radians(DoA_phi)),
                                      np.sin(np.radians(DoA_theta)) * np.sin(np.radians(DoA_phi)),
                                      np.cos(np.radians(DoA_theta))])
    array_response_RX = np.exp(M_RX_ind @ gamma_RX)'''

def dft_codebook_upa(rows, cols):
    # DFT matrices for rows and columns
    w_row = dft_codebook(rows)
    w_col = dft_codebook(cols)
    
    # Create 2D codebook by outer product
    upa_codebook = np.kron(w_row, w_col)  # Kronecker product to create 2D beams
    return upa_codebook

def calc_omega(elevationAngles, azimuthAngles, normalizedAntDistance = 0.5):
    sinElevations = np.sin(elevationAngles)
    omegax = 2 * np.pi * normalizedAntDistance * sinElevations * np.cos(azimuthAngles)  #x
    omegay = 2 * np.pi * normalizedAntDistance * sinElevations * np.sin(azimuthAngles)  #y
    #omegay = 2 * np.pi * normalizedAntDistance * np.cos(elevationAngles)  #new          #z
    return np.matrix((omegax, omegay))

def calc_vec_i(i, omega, antenna_range):
    print('a ', omega[:, i])
    print('b ', omega[:, i].shape)
    vec = np.exp(1j * omega[:, i] * antenna_range)
    print('c ', np.matrix(np.kron(vec[1], vec[0])).shape)
    return np.matrix(np.kron(vec[1], vec[0]))

def getNarrowBandUPAMIMOChannel(departureElevation,departureAzimuth,arrivalElevation,arrivalAzimuth, p_gainsdB,
                                pathPhases, number_Tx_antennasX, number_Tx_antennasY, number_Rx_antennasX,
                                number_Rx_antennasY, normalizedAntDistance=0.5):
    """Uses UPAs at both TX and RX.
    Will assume that all 4 normalized distances (Tx and Rx, x and y) are the same.
    """
    number_Tx_antennas = number_Tx_antennasX * number_Tx_antennasY
    number_Rx_antennas = number_Rx_antennasX * number_Rx_antennasY
    departureElevation = np.deg2rad(departureElevation)
    departureAzimuth = np.deg2rad(departureAzimuth)
    arrivalElevation = np.deg2rad(arrivalElevation)
    arrivalAzimuth = np.deg2rad(arrivalAzimuth)

    numRays = np.shape(departureElevation)[0]
    #number_Rx_antennas is the total number of antenna elements of the array, idem Tx
    H = np.matrix(np.zeros((number_Rx_antennas, number_Tx_antennas)))

    path_gain = np.power(10, p_gainsdB / 10)

    #generate uniformly distributed random phase in radians
    if pathPhases is None:
        pathPhases = 2*np.pi * np.random.rand(len(path_gain))
    else:
        #convert from degrees to radians the phase obtained with simulator (InSite)
        pathPhases = np.deg2rad(pathPhases)

    #include phase information, converting gains in complex-values
    path_complexGains = path_gain * np.exp(1j * pathPhases)

    # recall that in the narrowband case, the time-domain H is the same as the
    # frequency-domain H
    # Each vector below has the x and y values for each ray. Example 2 x 25 dimension
    departure_omega = calc_omega(departureElevation, departureAzimuth, normalizedAntDistance)
    arrival_omega = calc_omega(arrivalElevation, arrivalAzimuth, normalizedAntDistance)

    rangeTx_x = np.arange(number_Tx_antennasX)
    rangeTx_y = np.arange(number_Tx_antennasY)
    rangeRx_x = np.arange(number_Rx_antennasX)
    rangeRx_y = np.arange(number_Rx_antennasY)
    
    # Normalization factors eq (7.25) Tse's book
    norm_Tx = 1/np.sqrt(number_Tx_antennasX * number_Tx_antennasY)  # Tx array normalization
    norm_Rx = 1/np.sqrt(number_Rx_antennasX * number_Rx_antennasY)  # Rx array normalization
    
    for ray_i in range(numRays):
        #departure
        vecx = np.exp(-1j * departure_omega[0,ray_i] * rangeTx_x)
        vecy = np.exp(-1j * departure_omega[1,ray_i] * rangeTx_y)
        departure_vec = norm_Tx * np.matrix(np.kron(vecx, vecy)) #1xn             #y x expands first x then y
        #arrival
        vecx = np.exp(-1j * arrival_omega[0,ray_i] * rangeRx_x)
        vecy = np.exp(-1j * arrival_omega[1,ray_i] * rangeRx_y)
        arrival_vec = norm_Rx * np.matrix(np.kron(vecx, vecy)) #1xn

        antenna_pattern_gain_Tx = 1
        antenna_pattern_gain_Rx = 1
        pattern_gain = antenna_pattern_gain_Tx * antenna_pattern_gain_Rx

        # eq (7.29) Tse's book 
        H = H + path_complexGains[ray_i] * pattern_gain * arrival_vec.T * departure_vec.conj()
    return H

def getCodebookOperatedChannel(H, Wt, Wr):
    if Wr is None: #only 1 antenna at Rx, and Wr was passed as None
        return H * Wt
    if Wt is None: #only 1 antenna at Tx
        return Wr.conj().T * H
    try:
        result = Wr.conj().T * H * Wt
    except Exception as e:
        print(f'ERROR: {e}')
    return result # return equivalent channel after precoding and combining

def rotate_vectors(azimuths, zeniths, alpha, beta, gamma):
    # Convert list to arrays numpy
    azimuths = np.array(azimuths)
    zeniths = np.array(zeniths)
    
    # Convert angles to radians
    alpha, beta, gamma = np.radians([alpha, beta, gamma])
    
    # Rotation matrix arround WI Z axis
    Rz = np.array([
        [np.cos(alpha), -np.sin(alpha), 0],
        [np.sin(alpha), np.cos(alpha), 0],
        [0, 0, 1]
    ])
    
    # Rotation matrix arround WI Y axis
    Ry = np.array([
        [np.cos(beta), 0, np.sin(beta)],
        [0, 1, 0],
        [-np.sin(beta), 0, np.cos(beta)]
    ])
    
    # Rotation matrix arround WI X axis
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(gamma), -np.sin(gamma)],
        [0, np.sin(gamma), np.cos(gamma)]
    ])
    
    # Total rotation matrix R = Rx * Ry * Rz
    R = Rx @ Ry @ Rz
    
    # Convert azimuth and zenith to cartesian coordinates
    x = np.sin(np.radians(zeniths)) * np.cos(np.radians(azimuths))
    y = np.sin(np.radians(zeniths)) * np.sin(np.radians(azimuths))
    z = np.cos(np.radians(zeniths))
    
    # Apply rotation
    rotated_vectors = R @ np.vstack((x, y, z))
    
    # Convert back to spherical coordinates
    rotated_zeniths = np.degrees(np.arccos(rotated_vectors[2]))
    rotated_azimuths = np.degrees(np.arctan2(rotated_vectors[1], rotated_vectors[0]))
    
    # Ensure that azimuths are in the range [0, 360]
    rotated_azimuths = np.mod(rotated_azimuths, 360)
    
    # Convert arrays to lists
    return rotated_azimuths.tolist(), rotated_zeniths.tolist()
    
def import_mimo_channel(H_csv):
    # Load CSV ignoring comment lines
    # csvName is a string
    df = pd.read_csv(H_csv, header=3)#comment="#", header=0 
    num_rx = df["<Rx Element>"].nunique()  # Count unique Rx elements
    num_tx = (df.shape[1] - 2) // 2  # Each Tx has 2 columns (real and imaginary)

    # Initialize matrix H (Rx x Tx) as an array of complex numbers
    H = np.zeros((num_rx, num_tx), dtype=complex)

    # Fill the matrix H
    for i, row in df.iterrows():
        rx_index = int(row["<Rx Element>"]) - 1  # Adjustment for index 0
        for tx_index in range(num_tx):
            real_part = row.iloc[2 + 2 * tx_index]  # Real column
            imag_part = row.iloc[3 + 2 * tx_index]  # Imaginary column
            H[rx_index, tx_index] = complex(real_part, imag_part)
    return H