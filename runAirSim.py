import os
import subprocess

path_to_AirSim_Executable = os.path.join(
    "C:",
    "Users",
    "takashi",
    "Documents",
    "UnrealProjects",
    "MyProject",
    "Executable",
    "WindowsNoEditor",
    "MyProject.exe",
)

# path_to_Wibatch_Executable = os.path.join(
#     "C:",
#     "'Program Files'",
#     "Remcom",
#     "'Wireless InSite 3.2.0.3'",
#     "bin",
#     "calc",
#     "wibatch.exe",
# )

subprocess.run(path_to_AirSim_Executable + " NewMap", shell=True, check=True)
