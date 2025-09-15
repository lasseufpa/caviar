# Getting started

\*Currently tested on Ubuntu 22.04

## Pre-requisites

| RAM | GPU | CPU |

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

    bash install.sh

## Executing a simulation

In the project root folder, run (use `--enable-monitor` flag to save parameters in Influx dB):

    ./caviar

To correctly abort a simulation, in the terminal press:

    ctrl+C
AddX2Interface
## Configuring the simulation

The configuration parameters used in the simulation are stored in `kernel/.config/config.json`

## Documentation

To correct build the documentation, please run:

    mkdocs serve

In your browser, search for: 

    localhost:8000
