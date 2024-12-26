import numpy as np


def dft_codebook(dim):
    seq = np.matrix(np.arange(dim))
    mat = seq.conj().T * seq
    w = np.exp(-1j * 2 * np.pi * mat / dim)
    return w


def generate_dft_codebook(codebook_dimension):
    """
    Generate discrete Fourier transform (DFT) codebooks.

    Parameters:
    codebook_dimension (int): The dimension of the DFT codebook.

    Returns:
    np.ndarray: The DFT codebook matrix.
    """
    n = np.arange(codebook_dimension)
    m = np.matrix(n)
    codebook = np.exp((-2j * np.pi * m.H * m) / codebook_dimension)
    return codebook


def generate_equivalent_channel(rx_antennas_num, tx_antennas_num, channelMatrix):
    """
    Applies precoding and combining and return the equivalent channel matrix.

    Args:
        rx_antennas_num (int): Number of receive antennas.
        tx_antennas_num (int): Number of transmit antennas.
        channelMatrix (numpy.ndarray): The original channel matrix.

    Returns:
        numpy.ndarray: The equivalent channel matrix after precoding and combining.
    """
    c_rx = generate_dft_codebook(rx_antennas_num)
    c_tx = generate_dft_codebook(tx_antennas_num)
    return c_rx.H * channelMatrix * c_tx
