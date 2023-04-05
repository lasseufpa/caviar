import mitsuba as mi
import drjit as dr
import xml.etree.ElementTree as ET
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Paths2CIR
import numpy as np
from obj_move import translate
import mimo_channels


def getRunMIMOdata(
    output_file, AoD_az, AoA_az, gain_in_dB, number_Tx_antennas, number_Rx_antennas
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


mi.set_variant("cuda_ad_rgb")
mitsuba_file = "/home/joao/codes/caviar/examples/sionna/simple_street_canyon/simple_street_canyon.xml"

rx_3D_object_name = "mesh-Cube"
rx_starting_x = -60.8888
rx_starting_y = -0.471238
rx_starting_z = 2.673

step_size = 15
number_of_steps = 2

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
        num_rows=32,
        num_cols=1,
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern="hw_dipole",
        polarization="V",
    )

    # Configure antenna array for all receivers
    scene.rx_array = PlanarArray(
        num_rows=8,
        num_cols=1,
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern="hw_dipole",
        polarization="cross",
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

    # Compute propagation paths
    paths = scene.compute_paths(
        max_depth=5,
        method="stochastic",  # For small scenes the method can be also set to "exhaustive"
        num_samples=1e6,  # Number of rays shot into random directions, too few rays can lead to missing paths
        seed=1,
    )  # By fixing the seed, reproducible results can be ensured

    # We can now access for every path the resulting transfer matrices, the propagation delay,
    # as well as the angles of departure and arrival, respectively (zenith and azimuth).
    mat_t, tau, theta_t, phi_t, theta_r, phi_r = paths.as_tuple()

    # print("Shape of mat_t:", mat_t.shape)

    # Let us inspect a specific path in detail
    path_idx = 0

    # The dimensions are batch_size, num_rx, num_tx, max_num_paths, 2, 2] where the transfer matrices have an additional 2x2 dimension
    # print(f"\n--- Detailed results for path {path_idx} ---\n")
    # print(f"Transfer matrix:\n{mat_t[0,0,0,path_idx,...]}")
    # print(f"\nPropagation delay: {tau[0,0,0,path_idx]*1e6:.5f} us\n")
    # print(f"Zenith angle of departure: {theta_t[0,0,0,path_idx]:.4f} rad")
    # print(f"Azimuth angle of departure: {phi_t[0,0,0,path_idx]:.4f} rad")
    # print(f"Zenith angle of arrival: {theta_r[0,0,0,path_idx]:.4f} rad")
    # print(f"Azimuth angle of arrival: {phi_r[0,0,0,path_idx]:.4f} rad")

    filename = f"/home/joao/codes/caviar/runs/run_{current_step}"

    scene.render_to_file(
        camera="scene-cam-0",  # Also try camera="preview"
        paths=paths,
        show_devices=True,
        show_paths=True,
        filename=f"{filename}.png",
        resolution=[650, 500],
    )
    ########################### COPIED FROM SIONNA EXAMPLE #####################

    L = mat_t.shape[3]  # Number of paths

    getRunMIMOdata(
        output_file=filename,
        AoD_az=theta_t,
        AoA_az=phi_r,
        gain_in_dB=np.array([L, 0]),
        number_Tx_antennas=64,
        number_Rx_antennas=4,
    )
