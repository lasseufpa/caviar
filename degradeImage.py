from PIL import Image as img
import numpy as np


rng = np.random.default_rng(1)


image = img.open("/home/joao/Downloads/airsimtest.png")
image_bytes = bytearray(image.tobytes())

width = 1
height = 1
bit_depth = 32
pixel_size_bytes = (width * height * bit_depth) / 8
image_size_bytes = len(image_bytes)

number_of_pixels_in_tcp_packet = 65536 / pixel_size_bytes

# packet_size_bytes = 65536  # Max size of a TCP packet = 64 KiB = 65536 bytes
packet_size_bytes = pixel_size_bytes
total_number_of_packets = image_size_bytes / packet_size_bytes
if type(total_number_of_packets) == float:
    total_number_of_packets = int(total_number_of_packets) + 1
packet_drop_rate = 0.1
packets_to_drop = int(packet_drop_rate * total_number_of_packets)
image_packets = np.array_split(image_bytes, total_number_of_packets)
# Gets different packages indexes to drop
dropped_package_indexes = rng.choice(
    total_number_of_packets, packets_to_drop, replace=False
)


# Zeroes the bytes of the dropped packages
for idx in dropped_package_indexes:
    for value_idx, value in enumerate(image_packets[idx]):
        image_packets[idx][value_idx] = 0


reconstructed_image_packets = np.array(image_packets)
reconstructed_image_packets = np.concatenate(reconstructed_image_packets).astype("b")

image_bytes_saveable = img.frombytes(
    mode="RGBA", size=image.size, data=reconstructed_image_packets, decoder_name="raw"
)
image_bytes_saveable.save("/home/joao/Downloads/fromBytes.png")
