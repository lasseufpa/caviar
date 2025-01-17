# Getting started

Here you find the code described in [borges2024caviar] (see below), which allows to generate the results in this paper.

\*Currently tested only on Ubuntu 22.04 and Python 3.9.16

## Pre-requisites

### Auxiliary linux packages

#### First update (if necessary)

    sudo apt update

#### cURL

    sudo apt install curl

#### Unzip

    sudo apt install unzip

### Setting up the NATS server

Go to https://github.com/nats-io/nats-server/tags , download the latest `.deb` release and install it.

## Installing

### 1) Clone the project repository

#### Using SSH:

    git clone git@github.com:lasseufpa/caviar.git

#### Using HTTP:

    git clone https://github.com/lasseufpa/caviar.git

### 2) Set up the 3D scenario

Go to the folder where the 3D executable will be stored:

```
cd caviar/3d
```

Download the executable

```
curl https://nextcloud.lasseufpa.org/s/zdNNfM2YCmfrHsi/download/central_park.zip --output central_park.zip

```

Unzip the file

```
unzip central_park.zip
```

Set it as an executable

    chmod +x ./central_park/LinuxNoEditor/central_park/Binaries/Linux/central_park-Linux-DebugGame

Now, go back to the project root

    cd ..

### 3) Install the requirements

We use python 3.9.16\*

(Optional): Create and activate a virtual environment with conda

```
conda create --name caviar python=3.9.16
```

```
conda activate caviar
```

First we should install the package below

```
pip install msgpack-rpc-python==0.4.1
```

After this, we install the rest of the requirements

```
pip install -r requirements.txt
```

## Executing a simulation

In the project root folder, run:

    python3 simulate.py

This will start a simulation of the flights defined in `caviar/examples/airsimTools/waypoints/trajectories/`

To correctly abort a simulation, in the terminal press:

    ctrl+C

## Configuring the simulation

The configuration parameters used in the simulation are stored in `caviar/caviar_config.py`

**More documentation on the configuration soon**

## Troubleshoot

#### On the first run, the drone was teleported to the street, but did not started to fly

Sometimes this error can happen due to the download of YOLO weights. For this case, just exit the current simulation with `ctrl+c` and try it again.

#### Got the error: "Can't find libdevice directory ${CUDA_DIR}/nvvm/libdevice. This may result in compilation or runtime failures, if the program we try to run uses routines from libdevice."

This is due to not being able to file the CUDA directory. For this you can execute the following, to add it to your environment variables:

##### For bash

    echo -e "export CUDA_DIR=\"$(whereis cuda | cut -d ' ' -f 2)\"\nexport XLA_FLAGS=--xla_gpu_cuda_data_dir=\"\${CUDA_DIR}\"" >> ~/.bashrc

##### For zsh

    echo -e "export CUDA_DIR=\"$(whereis cuda | cut -d ' ' -f 2)\"\nexport XLA_FLAGS=--xla_gpu_cuda_data_dir=\"\${CUDA_DIR}\"" >> ~/.zshrc

## Citation

If you benefit from this work, please cite on your publications using:

```
@ARTICLE{borges2024caviar,
  author={Borges, João and Bastos, Felipe and Correa, Ilan and Batista, Pedro and Klautau, Aldebaro},
  journal={IEEE Internet of Things Journal},
  title={{CAVIAR: Co-Simulation of 6G Communications, 3-D Scenarios, and AI for Digital Twins}},
  year={2024},
  volume={11},
  number={19},
  pages={31287-31300},
  doi={10.1109/JIOT.2024.3418675}}
```
