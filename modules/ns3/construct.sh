#!/bin/bash
#
# Copyright (c) 2023 Núcleo de P&D em Telecomunicações, Automação e Eletrônica (LASSE)
# Make sure you have docker installed on your system. 
#


if [[ $EUID -ne 0 ]];then
    echo "Need to be executed as sudo"
    exit 1
fi

# Check if the container exists
if docker ps -a --filter "name=gnb" --format '{{.Names}}' | grep -w "gnb" > /dev/null; then
    echo "Container 'gnb' already exists."
    # Check if the container is running
    if docker ps --filter "name=gnb" --format '{{.Names}}' | grep -w "gnb" > /dev/null; then
        echo "Container 'gnb' is already running."
    else
        echo "Starting container 'gnb'..."
        docker start gnb
    fi
else
    echo "Creating and starting container 'gnb'..."
    docker run -dt --privileged --name gnb ubuntu bash
    docker exec gnb apt update
    docker exec gnb apt install net-tools iproute2 iputils-ping -y
fi

# Install necessary packages in the container
