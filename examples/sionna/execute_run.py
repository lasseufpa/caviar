import os
import time
import numpy as np
import mitsuba as mi
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Paths2CIR, Camera
from sionna.channel import cir_to_ofdm_channel, subcarrier_frequencies
from obj_move import translate
import mimo_channels

# from examples.sionna.mimo_channels import getDFTOperatedChannel
# from examples.sionna.obj_move import translate


mi.set_variant("cuda_ad_rgb")

render_to_file = False
save_data = False

################################# Configure paths ##############################

current_dir = os.getcwd()
output_dir = os.path.join(current_dir, "runs")

mitsuba_file = os.path.join(
    current_dir,
    "examples",
    "sionna",
    "central_park",
    "central_park.xml",
)

################################# Configure Rx mobility parameters #############

rx_3D_object_name = "mesh-Cube"
rx_starting_x = 23.69
rx_starting_y = -3.351
rx_starting_z = 139

cam_x = -350
cam_y = 200
cam_z = 338.2

cam_angle_x = 250
cam_angle_y = -220
cam_angle_z = 0

################################# Configure Tx parameters #############
# Ground
# tx_x = -11
# tx_y = 69
# tx_z = 10

# Next to Rx
tx_x = 21.95
tx_y = -8.985
tx_z = 137

################################# Configure simulation parameters ##############

step_size = 15
number_of_steps = 1

nTx = 32
nRx = 8


def getRunMIMOdata(
    mimoChannel,
    number_Tx_antennas,
    number_Rx_antennas,
):
    equivalentChannel = mimo_channels.getDFTOperatedChannel(
        mimoChannel, number_Tx_antennas, number_Rx_antennas
    )

    equivalentChannelMagnitude = np.abs(equivalentChannel)

    best_ray = np.argwhere(
        equivalentChannelMagnitude == np.max(equivalentChannelMagnitude)
    )

    return mimoChannel, equivalentChannel, equivalentChannelMagnitude, best_ray


def run(current_step, new_x, new_y, new_z):
    translate(
        mitsuba_file, rx_3D_object_name, new_x, new_y, new_z
    )  # move the receiver 3D object
    rx_current_x = rx_starting_x + new_x
    rx_current_y = rx_starting_y + new_y
    rx_current_z = rx_starting_z + new_z
    scene = load_scene(mitsuba_file)  # Sionna scene
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
    tx = Transmitter(name="tx", position=[tx_x, tx_y, tx_z])

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

    # starting_instant = time.time()
    # Compute propagation paths
    paths = scene.compute_paths(
        max_depth=5,
        method="stochastic",  # For small scenes the method can be also set to "exhaustive"
        num_samples=1e6,  # Number of rays shot into random directions, too few rays can lead to missing paths
        seed=1,
    )  # By fixing the seed, reproducible results can be ensured
    # ending_instant = time.time()
    # print(f"RT duration: {ending_instant-starting_instant}")

    output_filename = os.path.join(current_dir, "runs", f"run_{str(current_step)}")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    mat_t, tau, theta_t, phi_t, theta_r, phi_r = paths.as_tuple()

    # print("Shape of mat_t:", mat_t.shape)

    if render_to_file:
        # Create new camera with different configuration
        my_cam = Camera(
            "my_cam",
            position=[cam_x, cam_y, cam_z],
            look_at=[cam_angle_x, cam_angle_y, cam_angle_z],
        )
        scene.add(my_cam)

        scene.render_to_file(
            camera="my_cam",
            paths=paths,
            show_devices=True,
            show_paths=True,
            filename=f"{output_filename}.png",
            resolution=[650, 500],
        )

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
    path_coefficients, path_delays = p2c(paths.as_tuple())

    # print("Shape of path_coefficients: ", path_coefficients.shape)
    # print("Shape of path_delays: ", path_delays.shape)

    # Compute frequencies of subcarriers and center around carrier frequency
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)

    # Compute the frequency response of the channel at frequencies.
    h_freq = cir_to_ofdm_channel(
        frequencies, path_coefficients, path_delays, normalize=True
    )  # Non-normalized includes path-loss

    # Verify that the channel is normalized
    # h_avg_power = tf.reduce_mean(tf.abs(h_freq) ** 2).numpy()

    # print("Average power h_freq: ", h_avg_power)  # Channel is normalized

    ########################### COPIED FROM SIONNA EXAMPLE #####################

    (
        mimoChannel,
        equivalentChannel,
        equivalentChannelMagnitude,
        best_ray,
    ) = getRunMIMOdata(
        mimoChannel=h_freq.numpy().squeeze()[:, :, 0, 0],
        number_Tx_antennas=nTx,
        number_Rx_antennas=nRx,
    )

    rx_airsim_position = [new_x, new_y, new_z]
    rx_starting_position = [rx_starting_x, rx_starting_y, rx_starting_z]
    rx_current_position = [rx_current_x, rx_current_y, rx_current_z]

    if save_data:
        np.savez(
            output_filename,
            path_coefficients=path_coefficients,
            path_delays=path_delays,
            rx_airsim_position=rx_airsim_position,
            rx_starting_position=rx_starting_position,
            rx_current_position=rx_current_position,
            mimoChannel=mimoChannel,
            equivalentChannel=equivalentChannel,
            equivalentChannelMagnitude=equivalentChannelMagnitude,
            best_ray=best_ray,
        )
    else:
        return (
            path_coefficients,
            path_delays,
            rx_airsim_position,
            rx_starting_position,
            rx_current_position,
            mimoChannel,
            equivalentChannel,
            equivalentChannelMagnitude,
            best_ray,
        )


if __name__ == "__main__":
    run(0, 0, 0, 0)
