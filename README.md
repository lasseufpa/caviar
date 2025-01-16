# Getting started

\*Currently tested on Ubuntu 22.04

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

---

(FOR WINDOWS):

Go to https://github.com/nats-io/nats-server/tags , download the latest `.exe` and place it on the project root folder, after cloning it.

---

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

---

(FOR WINDOWS): use the following link and manually download it:
https://nextcloud.lasseufpa.org/s/rt4YP5DxEybfYXo

---

Unzip the file

```
unzip central_park.zip
```

Set it as an executable

    chmod +x ./central_park/LinuxNoEditor/central_park/Binaries/Linux/central_park-Linux-DebugGame

### 3) Install the requirements

    pip install -r requirements.txt

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

Sometimes this error can happen, but just exit with `ctrl+c` and try it again.

#### Got the error: "Can't find libdevice directory ${CUDA_DIR}/nvvm/libdevice. This may result in compilation or runtime failures, if the program we try to run uses routines from libdevice."

This is due to not being able to file the CUDA directory. For this you can execute the following, to add it to your environment variables:

##### For bash

    echo -e "export CUDA_DIR=\"$(whereis cuda | cut -d ' ' -f 2)\"\nexport XLA_FLAGS=--xla_gpu_cuda_data_dir=\"\${CUDA_DIR}\"" >> ~/.bashrc

##### For zsh

    echo -e "export CUDA_DIR=\"$(whereis cuda | cut -d ' ' -f 2)\"\nexport XLA_FLAGS=--xla_gpu_cuda_data_dir=\"\${CUDA_DIR}\"" >> ~/.zshrc

## Citation

If you benefit from this work on a publicaton, please cite using:

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
