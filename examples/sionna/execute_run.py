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

render_to_file = True
save_data = True

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

################################# Configure Tx parameters #############
# Ground
tx_x = -108
tx_y = -33
tx_z = 15

################################# Configure camera parameters #############

# cam_x = rx_x
# cam_y = rx_y
cam_z = 700

################################# Configure simulation parameters ##############

step_size = 15
number_of_steps = 1

nTx = 64
nRx = 4


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
        num_rows=int(np.sqrt(nTx)),
        num_cols=int(np.sqrt(nTx)),
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern="tr38901",
        polarization="V",
    )

    # Configure antenna array for all receivers
    scene.rx_array = PlanarArray(
        num_rows=int(np.sqrt(nRx)),
        num_cols=int(np.sqrt(nRx)),
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern="tr38901",
        polarization="V",
    )

    tx = Transmitter(
        name="tx", position=[tx_x, tx_y, tx_z], orientation=[-2.0944, 0.261799, 0]
    )

    scene.add(tx)

    rx = Receiver(
        name="rx",
        position=[rx_current_x, rx_current_y, rx_current_z - 10],
        orientation=[-0.523599, 0, 0],
    )

    scene.add(rx)

    scene.frequency = 40e9  # Frequency in Hz

    scene.synthetic_array = True  # If set to False, ray tracing will be done per antenna element (slower for large arrays)
    # cm = scene.coverage_map(max_depth=5,
    #                     cm_cell_size=(3., 3.), # Grid size of coverage map cells in m
    #                     combining_vec=None,
    #                     precoding_vec=None,
    #                     num_samples=int(1e2))
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
    figures_output_filename = os.path.join(
        current_dir, "runs", "figures", f"run_{str(current_step)}.png"
    )
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if render_to_file:
        # Checks if figures output folder exists
        if not os.path.exists(os.path.dirname(figures_output_filename)):
            os.mkdir(os.path.dirname(figures_output_filename))
        # Create new camera with different configuration
        my_cam = Camera(
            "my_cam",
            position=[rx_current_x, rx_current_y, cam_z],
            look_at=[rx_current_x, rx_current_y, rx_current_z],
        )
        scene.add(my_cam)

        scene.render_to_file(
            camera="my_cam",
            paths=paths,
            # coverage_map=cm,
            show_devices=True,
            show_paths=True,
            filename=figures_output_filename,
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

    # Compute frequencies of subcarriers and center around carrier frequency
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)

    # Compute the frequency response of the channel at frequencies.
    h_freq = cir_to_ofdm_channel(
        frequencies, path_coefficients, path_delays, normalize=True
    )  # Non-normalized includes path-loss

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
