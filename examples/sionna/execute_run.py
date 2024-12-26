import os
import time
import numpy as np
import mitsuba as mi
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Camera
from sionna.channel import cir_to_ofdm_channel
from obj_move import translate
import mimo_channels
from calc_time import getBitRate
from realtime_plot import plot_throughput
from joblib import load
from run_obj_unreal import plot_beam_interaction
import sys

sys.path.append("./")
import caviar_config

mi.set_variant("cuda_ad_rgb")

################################################################################
save_rt_paths_as_txt = caviar_config.save_rt_paths_as_txt
plot_beam = caviar_config.plot_beam
save_sionna_3d_scenes_as_png = caviar_config.save_sionna_3d_scenes_as_png
plot_realtime_throughput = caviar_config.plot_realtime_throughput
save_all_data_as_npz = caviar_config.save_all_data_as_npz
rx_number = caviar_config.rx_number
################################# Configure paths ##############################

current_dir = os.getcwd()
output_dir = os.path.join(current_dir, "runs")

scene_file_name = caviar_config.scene_file_name

scene_file = os.path.join(
    current_dir,
    "examples",
    "sionna",
    scene_file_name,
    scene_file_name + ".xml",
)

################################# Configure Rx mobility parameters #############

rx_3D_object_name = caviar_config.rx_3D_object_name
rx_starting_x = caviar_config.rx_starting_x
rx_starting_y = caviar_config.rx_starting_y
rx_starting_z = caviar_config.rx_starting_z

################################# Configure Tx parameters #############
# Ground
tx_x = caviar_config.tx_x
tx_y = caviar_config.tx_y
tx_z = caviar_config.tx_z  # 5m above roof

# Rotation parameters in radians, as defined in
# https://nvlabs.github.io/sionna/api/rt.html#sionna.rt.Transmitter
tx_alpha = caviar_config.tx_alpha
tx_beta = caviar_config.tx_beta
tx_gamma = caviar_config.tx_gamma

################################# Configure Rx parameters #############

rx_alpha = caviar_config.rx_alpha
rx_beta = caviar_config.rx_beta
rx_gamma = caviar_config.rx_gamma

################################# Configure camera parameters #############

# cam_x = rx_x
# cam_y = rx_y
cam_z = caviar_config.cam_z

################################# Configure simulation parameters ##############

step_size = caviar_config.step_size
number_of_steps = caviar_config.number_of_steps

nTx = caviar_config.nTx
nRx = caviar_config.nRx

rng = np.random.default_rng(caviar_config.random_seed)
all_best_bit_rate_Gbps = []
all_random_bit_rate_Gbps = []
all_predicted_bit_rate_Gbps = []


def getRunMIMOdata(
    mimoChannel,
    number_Tx_antennas,
    number_Rx_antennas,
):
    if rx_number > 1:
        for rx_index in range(rx_number):
            current_rx_mimoChannel = mimoChannel[rx_index]

            equivalentChannel = mimo_channels.generate_equivalent_channel(
                number_Rx_antennas, number_Tx_antennas, current_rx_mimoChannel
            )

            equivalentChannelMagnitude = np.abs(equivalentChannel)

            best_ray = np.argwhere(
                equivalentChannelMagnitude == np.max(equivalentChannelMagnitude)
            )
    else:
        current_rx_mimoChannel = mimoChannel

        equivalentChannel = mimo_channels.generate_equivalent_channel(
            number_Rx_antennas, number_Tx_antennas, current_rx_mimoChannel
        )
        equivalentChannelMagnitude = np.abs(equivalentChannel)
        best_ray = np.argwhere(
            equivalentChannelMagnitude == np.max(equivalentChannelMagnitude)
        )

    return (
        current_rx_mimoChannel,
        equivalentChannel,
        equivalentChannelMagnitude,
        best_ray,
    )


def run(current_step, new_x, new_y, new_z):
    translate(
        scene_file, rx_3D_object_name, new_x, new_y, new_z
    )  # move the receiver 3D object
    rx_current_x = rx_starting_x + new_x
    rx_current_y = rx_starting_y + new_y
    rx_current_z = rx_starting_z + new_z
    scene = load_scene(scene_file)

    scene.tx_array = PlanarArray(
        num_rows=int(np.sqrt(nTx)),
        num_cols=int(np.sqrt(nTx)),
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern=caviar_config.tx_antenna_pattern,
        polarization=caviar_config.tx_antenna_polarization,
    )

    scene.rx_array = PlanarArray(
        num_rows=int(np.sqrt(nRx)),
        num_cols=int(np.sqrt(nRx)),
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern=caviar_config.rx_antenna_pattern,
        polarization=caviar_config.rx_antenna_polarization,
    )

    tx = Transmitter(
        name="tx",
        position=[tx_x, tx_y, tx_z],
        orientation=[tx_alpha, tx_beta, tx_gamma],
    )

    scene.add(tx)

    for rx_index in range(rx_number):
        rx = Receiver(
            name="rx" + str(rx_index),
            position=[rx_current_x, rx_current_y, rx_current_z - 3 + rx_index],
            orientation=[rx_alpha, rx_beta, rx_gamma],
        )

        scene.add(rx)

    scene.frequency = caviar_config.carrier_frequency  # Carrier frequency (Hz)

    scene.synthetic_array = True
    # cm = scene.coverage_map(max_depth=5,
    #                     cm_cell_size=(3., 3.), # Grid size of coverage map cells in m
    #                     combining_vec=None,
    #                     precoding_vec=None,
    #                     num_samples=int(1e2))
    # starting_instant = time.time()
    # Compute propagation paths
    paths = scene.compute_paths(
        max_depth=5,
        method="fibonacci",
        num_samples=1e6,
        reflection=True,
        diffraction=True,
        scattering=True,
    )
    # ending_instant = time.time()
    # print(f"RT duration: {ending_instant-starting_instant}")

    # -------------------------------------------------------------------------------------------------------------------------------

    path_coefficients, path_delays = paths.cir(los=False)  # Get only NLOS paths

    number_of_paths = path_coefficients.numpy().shape[5]

    # Get the channel frequency response
    h_matrix = cir_to_ofdm_channel(
        [0.0], path_coefficients, path_delays, normalize=True
    )

    # -------------------------------------------------------------------------------------------------------------------------------
    (
        mimoChannel,
        equivalentChannel,
        equivalentChannelMagnitude,
        best_ray,
    ) = getRunMIMOdata(
        mimoChannel=h_matrix.numpy().squeeze()[:, :],
        number_Tx_antennas=nTx,
        number_Rx_antennas=nRx,
    )

    rx_airsim_position = [new_x, new_y, new_z]
    rx_starting_position = [rx_starting_x, rx_starting_y, rx_starting_z]
    rx_current_position = [rx_current_x, rx_current_y, rx_current_z]

    # Get bit rate
    bit_rate = getBitRate(equivalentChannelMagnitude, bandwidth=40e6)
    bit_rate_Gbps = bit_rate / 1e9  # Converts to Gbps
    # bit_rate_Gbps = bit_rate_Gbps / 10 # Divides the throughput between 10 drones in a hypothetical swarm
    best_ray_rx = best_ray[0][0]
    best_ray_tx = best_ray[0][1]
    best_bit_rate_Gbps = bit_rate_Gbps[best_ray_rx, best_ray_tx]
    random_bit_rate_Gbps = bit_rate_Gbps[rng.integers(0, 4), rng.integers(0, 64)]
    clf = load("trained_model.joblib")
    enc = load("trained_encoder.joblib")
    pred_beam_index = enc.inverse_transform(
        clf.predict(np.array([rx_current_position]))
    )[0][1:-1].split(",")
    predicted_bit_rate_Gbps = bit_rate_Gbps[
        int(pred_beam_index[0]), int(pred_beam_index[1])
    ]

    all_best_bit_rate_Gbps.append(best_bit_rate_Gbps * int(1e3))
    all_random_bit_rate_Gbps.append(random_bit_rate_Gbps * int(1e3))
    all_predicted_bit_rate_Gbps.append(predicted_bit_rate_Gbps * int(1e3))

    output_filename = os.path.join(current_dir, "runs", f"run_{str(current_step)}")
    figures_output_filename = os.path.join(current_dir, "runs", "figures", f"run_0.png")

    if number_of_paths > 0:
        print(
            f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {number_of_paths} paths obtained during this run"
        )
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if save_sionna_3d_scenes_as_png:
            # Checks if figures output folder exists
            if not os.path.exists(os.path.dirname(figures_output_filename)):
                os.mkdir(os.path.dirname(figures_output_filename))
            # Create new camera with different configuration
            topview_cam = Camera(
                "topview_cam",
                position=[rx_current_x, rx_current_y, cam_z],
                look_at=[rx_current_x, rx_current_y, rx_current_z],
            )
            scene.add(topview_cam)

            scene.render_to_file(
                camera="topview_cam",
                paths=paths,
                # coverage_map=cm,
                show_devices=True,
                show_paths=True,
                filename=figures_output_filename,
                resolution=[325, 250],
            )

        if save_rt_paths_as_txt:
            paths_visualization_output = os.path.join(
                current_dir, "runs", "paths", f"run_{str(current_step)}.txt"
            )
            # Checks if figures output folder exists
            if not os.path.exists(os.path.dirname(paths_visualization_output)):
                os.mkdir(os.path.dirname(paths_visualization_output))
            paths.export(paths_visualization_output)
            if plot_beam:
                plot_beam_interaction(paths_visualization_output)

        if plot_realtime_throughput:
            plot_throughput(
                float(current_step),
                best_bit_rate_Gbps * int(1e3),
                predicted_bit_rate_Gbps * int(1e3),
                random_bit_rate_Gbps * int(1e3),
                np.mean(all_best_bit_rate_Gbps[-10:]),
                np.mean(all_predicted_bit_rate_Gbps[-10:]),
                np.mean(all_random_bit_rate_Gbps[-10:]),
            )

        if save_all_data_as_npz:
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
                bit_rate=bit_rate,
                best_bit_rate_Gbps=best_bit_rate_Gbps,
                random_bit_rate_Gbps=random_bit_rate_Gbps,
            )
    else:
        print(
            ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> No paths obtained during this run"
        )

    del paths  # deallocation of memory

    # return best_bit_rate_Gbps
    # return predicted_bit_rate_Gbps
    return random_bit_rate_Gbps


if __name__ == "__main__":
    run(0, 0, 0, 0)
