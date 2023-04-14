import os
import numpy as np
import tensorflow as tf
import mitsuba as mi
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Paths2CIR, Camera
from sionna.channel import (
    cir_to_ofdm_channel,
    subcarrier_frequencies,
    OFDMChannel,
    ApplyOFDMChannel,
    CIRDataset,
)
from obj_move import translate
import mimo_channels

mi.set_variant("cuda_ad_rgb")

################################# Configure paths ##############################

current_dir = os.getcwd()
output_dir = os.path.join(current_dir, "runs")

central_park_path = os.path.join(
    current_dir,
    "examples",
    "sionna",
    "central_park",
    "central_park.xml",
)

mitsuba_file = central_park_path

################################# Configure Rx mobility parameters #############

rx_3D_object_name = "mesh-Cube"
rx_starting_x = -229.3
rx_starting_y = 588
rx_starting_z = 494.3

################################# Configure simulation parameters ##############

step_size = 15
number_of_steps = 1

nTx = 32
nRx = 8


def getRunMIMOdata(
    output_file,
    mimoChannel,
    # AoD_az,
    # AoA_az,
    # gain_in_dB,
    number_Tx_antennas,
    number_Rx_antennas,
):
    # mimoChannel = mimo_channels.getNarrowBandULAMIMOChannel(
    #     AoD_az, AoA_az, gain_in_dB, number_Tx_antennas, number_Rx_antennas
    # )

    equivalentChannel = mimo_channels.getDFTOperatedChannel(
        mimoChannel, number_Tx_antennas, number_Rx_antennas
    )

    equivalentChannelMagnitude = np.abs(equivalentChannel)

    best_ray = np.argwhere(
        equivalentChannelMagnitude == np.max(equivalentChannelMagnitude)
    )

    np.savez(
        output_file,
        mimoChannel=mimoChannel,
        equivalentChannel=equivalentChannel,
        equivalentChannelMagnitude=equivalentChannelMagnitude,
        best_ray=best_ray,
    )

    return mimoChannel, equivalentChannel, equivalentChannelMagnitude, best_ray


for current_step in range(number_of_steps):
    translate(
        mitsuba_file, rx_3D_object_name, -(current_step * step_size), 0, 0
    )  # move the receiver 3D object
    rx_current_x = -(rx_starting_x + (current_step * step_size))
    rx_current_y = rx_starting_y
    rx_current_z = rx_starting_z
    scene = load_scene(mitsuba_file)  # Sionna scene
    # rx_current_y = rx_starting_y + (current_step * step_size)
    # rx_current_z = rx_starting_z + (current_step * step_size)
    ########################### COPIED FROM SIONNA EXAMPLE #####################
    # Configure antenna array for all transmitters
    scene.tx_array = PlanarArray(
        num_rows=nTx,
        num_cols=1,
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern="tr38901",
        polarization="V",
    )

    # Configure antenna array for all receivers
    scene.rx_array = PlanarArray(
        num_rows=nRx,
        num_cols=1,
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern="tr38901",
        polarization="V",
    )

    # Create transmitter
    tx = Transmitter(name="tx", position=[-62.11, -8.71, 22])

    # Add transmitter instance to scene
    scene.add(tx)

    # Create a receiver

    rx = Receiver(
        name="rx",
        position=[rx_current_x, rx_current_y, rx_current_z],
        orientation=[0, 0, 0],
    )

    # Add receiver instance to scene
    scene.add(rx)

    tx.look_at(rx)  # Transmitter points towards receiver

    scene.frequency = 40e9  # in Hz; implicitly updates RadioMaterials

    scene.synthetic_array = True  # If set to False, ray tracing will be done per antenna element (slower for large arrays)

    # # Compute propagation paths
    # paths = scene.compute_paths(
    #     max_depth=5,
    #     method="stochastic",  # For small scenes the method can be also set to "exhaustive"
    #     num_samples=10,  # Number of rays shot into random directions, too few rays can lead to missing paths
    #     seed=1,
    # )  # By fixing the seed, reproducible results can be ensured

    output_filename = os.path.join(current_dir, "runs", f"run_{str(current_step)}")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Create new camera with different configuration
    my_cam = Camera("my_cam", position=[-228.7, 589.5, 688.8], look_at=[0, 0, 90])
    scene.add(my_cam)

    scene.render_to_file(
        camera="my_cam",
        # paths=paths,
        show_devices=True,
        # show_paths=True,
        filename=f"{output_filename}.png",
        resolution=[650, 500],
    )

    # --------------------------------------------------------------------------
    # We can now access for every path the resulting transfer matrices, the propagation delay,
    # as well as the angles of departure and arrival, respectively (zenith and azimuth).
    # mat_t, tau, theta_t, phi_t, theta_r, phi_r = paths.as_tuple()

    # print("Shape of mat_t:", mat_t.shape)

    # Let us inspect a specific path in detail
    # path_idx = 0

    # The dimensions are batch_size, num_rx, num_tx, max_num_paths, 2, 2] where the transfer matrices have an additional 2x2 dimension
    # print(f"\n--- Detailed results for path {path_idx} ---\n")
    # print(f"Transfer matrix:\n{mat_t[0,0,0,path_idx,...]}")
    # print(f"\nPropagation delay: {tau[0,0,0,path_idx]*1e6:.5f} us\n")
    # print(f"Zenith angle of departure: {theta_t[0,0,0,path_idx]:.4f} rad")
    # print(f"Azimuth angle of departure: {phi_t[0,0,0,path_idx]:.4f} rad")
    # print(f"Zenith angle of arrival: {theta_r[0,0,0,path_idx]:.4f} rad")
    # print(f"Azimuth angle of arrival: {phi_r[0,0,0,path_idx]:.4f} rad")
    # --------------------------------------------------------------------------

    # Default parameters in the PUSCHConfig
    subcarrier_spacing = 15e3
    fft_size = 48

    # Configure a Paths2CIR instance
    p2c = Paths2CIR(
        sampling_frequency=subcarrier_spacing,  # Set to 15e3 Hz
        num_time_steps=14,  # Number of OFDM symbols
        scene=scene,
    )

    # Transform paths into channel impulse responses
    a, tau = p2c(paths.as_tuple())

    print("Shape of a: ", a.shape)
    print("Shape of tau: ", tau.shape)

    # Compute frequencies of subcarriers and center around carrier frequency
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)

    # Compute the frequency response of the channel at frequencies.
    h_freq = cir_to_ofdm_channel(
        frequencies, a, tau, normalize=True
    )  # Non-normalized includes path-loss

    # Verify that the channel is normalized
    h_avg_power = tf.reduce_mean(tf.abs(h_freq) ** 2).numpy()

    print("Shape of h_freq: ", h_freq.shape)
    print("Average power h_freq: ", h_avg_power)  # Channel is normalized

    ########################### COPIED FROM SIONNA EXAMPLE #####################

    L = a.shape[5]  # Number of paths

    getRunMIMOdata(
        output_file=output_filename,
        mimoChannel=h_freq.numpy().squeeze()[:, :, 0, 0],
        # AoD_az=theta_t,
        # AoA_az=phi_r,
        # gain_in_dB=np.array([L, 0]),
        number_Tx_antennas=nTx,
        number_Rx_antennas=nRx,
    )
