import airsim
# If isOnline == true, the beamselection will be performed with the AirSim simulation.
isOnline = True

# Path for the AirSim waypoints file, to be used with online simulations
#airsim_path_file = "./path1.csv"
airsim_path_file = "./paths/trajectories/path1.csv"

# Path for the record file, to be used with stand alone simulations
record_file = "./record1.csv"

# Array with the UAV's IDs that are in the Airsim settings file (for the online simulations)
drone_ids = ["uav1"]
cam_types = [airsim.ImageType.Scene, airsim.ImageType.DepthVis, airsim.ImageType.Segmentation]
panoramic = True
cam_poses = [airsim.Pose(airsim.Vector3r(-205,-162,40), airsim.to_quaternion(-30,0,45)), airsim.Pose(airsim.Vector3r(-205,-162,40), airsim.to_quaternion(-30,0,180))]

initial_pose_offset = [14,-28,8.4]

# Array with the IDs of others mobile objects in the simulation, that are not controled by AirSim (for the online simulations)
ue_objects = ["simulation_car1", "simulation_car2", "simulation_pedestrian1", "simulation_pedestrian2", "simulation_pedestrian3", "simulation_pedestrian4", "simulation_pedestrian5", "simulation_pedestrian6", "simulation_pedestrian7", "simulation_pedestrian8", "simulation_pedestrian9", "simulation_pedestrian10", "simulation_pedestrian11", "simulation_pedestrian12", "simulation_pedestrian13", "simulation_pedestrian14", "simulation_pedestrian15", "simulation_pedestrian16", "simulation_pedestrian17", "simulation_pedestrian18", "simulation_pedestrian19", "simulation_pedestrian20", "simulation_pedestrian21", "simulation_pedestrian22", "simulation_pedestrian23", "simulation_pedestrian24", "simulation_pedestrian25", "simulation_pedestrian26", "simulation_pedestrian27", "simulation_pedestrian28", "simulation_pedestrian29", "simulation_pedestrian30","simulation_pedestrian31", "simulation_pedestrian32", "simulation_pedestrian33", "simulation_pedestrian34"]

pedestrians = ["person10_41","person07","person01_20","person05_23", "person04_22", "person06_24","person02_21","person08_30","person09_36"]
