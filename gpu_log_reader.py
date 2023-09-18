import numpy as np
from pathlib import Path
import os

cwd = os.getcwd()

onlytxt = [f for f in os.listdir(cwd) if f[-3:] == "txt"]

for txt in onlytxt:
    file = open(txt, "r")

    output_name = Path(file.name).stem + ".npz"

    central_park_cpu = []
    central_park_ram = []
    python_cpu = []
    python_ram = []
    for line in file:
        contents = line.split()
        if contents[-1] == "central_park-Li":
            central_park_cpu.append(int(contents[3]) if contents[3] != "-" else int(0))
            central_park_ram.append(int(contents[4]) if contents[3] != "-" else int(0))
        if contents[-1] == "python":
            python_cpu.append(int(contents[3]) if contents[3] != "-" else int(0))
            python_ram.append(int(contents[4]) if contents[3] != "-" else int(0))

    np.savez(
        output_name,
        central_park_cpu=central_park_cpu,
        central_park_ram=central_park_ram,
        python_cpu=python_cpu,
        python_ram=python_ram,
    )
