
# Getting Started

*Currently tested on Ubuntu 22.04*

## Prerequisites

| CPU | RAM  | GPU  |
| :-----: | :-----------: | :-----------: |
| 13th Gen Intel® Core™ i7-13700HX × 24 | 32,0 GiB     | RTX 4060 |



### Auxiliary Linux Packages

#### First Update (if necessary)

    sudo apt update

#### curl

    sudo apt install curl

#### unzip

    sudo apt install unzip

## Installation

### 1) Clone the Project Repository

#### Using SSH

    git clone git@github.com:lasseufpa/caviar.git

#### Using HTTP

    git clone https://github.com/lasseufpa/caviar.git

### 2) Install the Requirements

Use the provided bash script to install the requirements:

    source install.sh

## Running a Simulation

In the project root folder, run the following command (use the `--enable-monitor` flag to save parameters in InfluxDB):

    ./caviar

To properly abort a simulation, press the following in the terminal:

    ctrl+C

## Configuring the Simulation

The configuration parameters used in the simulation are stored in `kernel/.config/config.json`.

## Documentation

To build the documentation, please run:

    mkdocs serve

In your browser, go to:

    localhost:8000

## Citation

If you benefit from this work, please cite it in your publications using:

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