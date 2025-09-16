#!/bin/bash

set -e  # Exit on any error
set -o pipefail

# Check if OS is Linux or macOS
if [[ "$OSTYPE" != "linux-gnu"* && "$OSTYPE" != "darwin"* ]]; then
    echo "This script is only supported on Linux and macOS."
    exit 1
fi

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda not found. Please install Anaconda or Miniconda first."
    exit 1
fi

# Get the environment name from environment.yml
ENV_NAME=$(grep -m 1 "^name:" environment.yml | cut -d ' ' -f2)

# Check if the conda environment already exists
if conda env list | grep -qw "$ENV_NAME"; then
    echo "Conda environment '$ENV_NAME' already exists. Skipping creation."
else
    echo "Creating conda environment '$ENV_NAME' from environment.yml..."
    conda env create -f environment.yml
    echo "Conda environment '$ENV_NAME' created successfully."
fi

# Initialize conda (in case it's not)
eval "$(conda shell.bash hook)"

# Activate the conda environment
conda activate "$ENV_NAME" || {
    echo "Failed to activate conda environment '$ENV_NAME'."
}

# Function to install a package if missing
install_if_missing() {
    local cmd="$1"
    local pkg_linux="$2"
    local pkg_mac="$3"
    local friendly_name="$4"

    if ! command -v "$cmd" &> /dev/null; then
        echo "$friendly_name not found. Installing..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y "$pkg_linux"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install "$pkg_mac"
        fi
    else
        echo "$friendly_name is already installed."
    fi
}


install_if_missing docker docker.io --cask docker "Docker"
install_if_missing docker-compose docker-compose docker-compose "Docker Compose"
install_if_missing ffmpeg ffmpeg ffmpeg "FFmpeg"

# Install NATS server (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! command -v nats-server &> /dev/null; then
        echo "NATS server not found. Installing NATS server v2.11.9..."
        NATS_DEB_URL="https://github.com/nats-io/nats-server/releases/download/v2.11.9/nats-server-v2.11.9-386.deb"
        NATS_DEB_FILE="nats-server-v2.11.9-386.deb"
        wget -O "$NATS_DEB_FILE" "$NATS_DEB_URL"
        sudo dpkg -i "$NATS_DEB_FILE" || sudo apt-get install -f -y
        rm -f "$NATS_DEB_FILE"
        echo "NATS server installed."
    else
        echo "NATS server is already installed."
    fi
fi

# Install 3D scene (Linux only)
echo "Downloading 3D NTN urban scene..."
curl -L https://nextcloud.lasseufpa.org/s/9yj6D9sw3LxpQXK/download/3d-urban.zip --output modules/airsim/3d/ntn-urban.zip
unzip modules/airsim/3d/ntn-urban.zip -d modules/airsim/
rm modules/airsim/3d/ntn-urban.zip
echo "3D NTN urban scene downloaded and extracted."
chmod +x modules/airsim/3d/ProjectOne/Binaries/Linux/ProjectOne

# Init submodules
git submodule update --init --recursive
