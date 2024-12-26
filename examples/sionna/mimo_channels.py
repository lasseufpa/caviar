import numpy as np


def dft_codebook(dim):
    seq = np.matrix(np.arange(dim))
    mat = seq.conj().T * seq
    w = np.exp(-1j * 2 * np.pi * mat / dim)
    return w


def getDFTOperatedChannel(H, number_Tx_antennas, number_Rx_antennas):
    wt = dft_codebook(number_Tx_antennas)
    wr = dft_codebook(number_Rx_antennas)
    dictionaryOperatedChannel = wr.conj().T * H * wt
    return dictionaryOperatedChannel  # return equivalent channel after precoding and combining
