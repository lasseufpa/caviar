def get_time_for_rescue(throughput):
    """
    This function calculates the time in seconds to transmit
    rescue images and finish the rescue.

    The rescue will finish after transmiting 10 pictures of 4 MB
    (4 MiB = 3.355e7 bits)
    """
    data_to_transmit_in_bits = 3.355e7 * 10
    time_to_tx = data_to_transmit_in_bits / (throughput)
    return time_to_tx
