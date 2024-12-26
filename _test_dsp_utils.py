import numpy as np

from examples.sionna.dsp_utils import generate_dft_codebook


# Legacy function from https://github.com/lasseufpa/5gm-data/blob/master/mimo_channels.py#L21
# This function is GPL-3.0 licensed code. Do not commit to the CAVIAR repository.
# CAVIAR instead uses the function generate_dft_codebook()
def dft_codebook(dim):
    seq = np.matrix(np.arange(dim))
    mat = seq.conj().T * seq
    w = np.exp(-1j * 2 * np.pi * mat / dim)
    return w


if __name__ == "__main__":
    # Checking the similarity of the legacy and the new implementation
    for input in range(1, 1000):
        if not np.allclose(dft_codebook(input), generate_dft_codebook(input)):
            print(f"Mismatch found for input: {input}")
            break
    else:
        print("Results matched for all inputs up to 1000")
