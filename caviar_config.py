import airsim


# Path for the record file, to be used with standalone simulations
record_file = "./record1.csv"

# Array with the UAV's IDs that are
# in the Airsim settings file (for the online simulations)
drone_ids = ["uav1"]
cam_types = [
    airsim.ImageType.Scene,
    airsim.ImageType.DepthVis,
    airsim.ImageType.Segmentation,
]
panoramic = True
cam_poses = [
    airsim.Pose(airsim.Vector3r(-205, -162, 40), airsim.to_quaternion(-30, 0, 45)),
    airsim.Pose(airsim.Vector3r(-205, -162, 40), airsim.to_quaternion(-30, 0, 180)),
]

initial_pose_offset = [14, -28, 8.4]

# Available pedestrian models
pedestrians = [
    "person10_41",
    "person07",
    "person01_20",
    "person05_23",
    "person04_22",
    "person06_24",
    "person02_21",
    "person08_30",
    "person09_36",
]

################################################################################
# execute_run.py configuration
save_rt_paths_as_txt = False
save_sionna_3d_scenes_as_png = False
save_all_data_as_npz = False
plot_beam = False
plot_realtime_throughput = False
scene_file_name = "central_park"
rx_3D_object_name = "mesh-Cube"
rx_starting_x = 23.69
rx_starting_y = -3.351
rx_starting_z = 139
rx_alpha = -0.523599
rx_beta = 0
rx_gamma = 0
rx_antenna_pattern = "tr38901"
rx_antenna_polarization = "V"
tx_x = -154
tx_y = 64
tx_z = 120
tx_alpha = -2.0944
tx_beta = 0.785398
tx_gamma = 0
tx_antenna_pattern = "tr38901"
tx_antenna_polarization = "V"
step_size = 15
number_of_steps = 1
nTx = 64
nRx = 4
random_seed = 1
carrier_frequency = 40e9
cam_z = 700
rx_number = 1
################################################################################
# caviar_integration.py configuration
is_sync = True
is_rescue_mission = True
simulation_time_step = 0.5
save_multimodal = False
