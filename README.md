# Getting started

\*Currently tested on Ubuntu 22.04

## Pre-requisites

| CPU | RAM  | GPU  |
| :-----: | :-----------: | :-----------: |
| 13th Gen Intel® Core™ i7-13700HX × 24 | 32,0 GiB     | RTX 4060 |

### Auxiliary linux packages

#### First update (if necessary)

    sudo apt update

#### cURL

    sudo apt install curl

#### Unzip

    sudo apt install unzip

## Installing

### 1) Clone the project repository

#### Using SSH:

    git clone git@github.com:lasseufpa/caviar.git

#### Using HTTP:

    git clone https://github.com/lasseufpa/caviar.git

### 3) Install the requirements

Use the bash file script to install the requirements

    source install.sh

## Executing a simulation

In the project root folder, run (use `--enable-monitor` flag to save parameters in Influx dB):

    ./caviar

To correctly abort a simulation, in the terminal press:

    ctrl+C

## Configuring the simulation

The configuration parameters used in the simulation are stored in `kernel/.config/config.json`

## Documentation

To correct build the documentation, please run:

    mkdocs serve

In your browser, search for: 

    localhost:8000

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