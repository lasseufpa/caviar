from PIL import Image as img
import numpy as np
import time


rng = np.random.default_rng(1)
image = img.open("/home/joaoborges/Downloads/airsimtest.png")


def dropPacketsFromImage(image, packet_drop_rate, output_folder="/home/joaoborges/Downloads/fromBytes.png", packet_size_bytes=pixel_size_bytes, rng=rng):
    width = 1
    height = 1
    bit_depth = 32
    pixel_size_bytes = (width * height * bit_depth) / 8
    # number_of_pixels_in_tcp_packet = 65536 / pixel_size_bytes
    # packet_size_bytes = pixel_size_bytes
    # packet_size_bytes = 65536  # Max size of a TCP packet = 64 KiB = 65536 bytes

    starting_instant = time.time()
    image_bytes = bytearray(image.tobytes())
    image_size_bytes = len(image_bytes)

    if image_size_bytes % packet_size_bytes != 0:
        raise Exception("not divisible")

    total_number_of_packets = image_size_bytes // int(packet_size_bytes)
    packets_to_drop = int(packet_drop_rate * total_number_of_packets)
    image_packets = np.array(image_bytes).reshape((total_number_of_packets,-1))
    # Gets different packages indexes to drop
    dropped_package_indexes = rng.choice(
        total_number_of_packets, packets_to_drop, replace=False
    )

    # Zeroes the bytes of the dropped packages
    image_packets[dropped_package_indexes] = 0

    reconstructed_image_packets = np.array(image_packets)
    reconstructed_image_packets = np.concatenate(reconstructed_image_packets).astype("b")

    image_bytes_saveable = img.frombytes(
        mode="RGBA", size=image.size, data=reconstructed_image_packets, decoder_name="raw"
    )

    image_bytes_saveable.save(output_folder)
    ending_instant = time.time()
    print(f"Duration: {ending_instant-starting_instant}")
