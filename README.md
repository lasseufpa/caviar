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
