#!/bin/bash
#
# Copyright (c) 2023 Núcleo de P&D em Telecomunicações, Automação e Eletrônica (LASSE)
# Make sure you have docker installed on your system. 
#


if [[ $EUID -ne 0 ]];then
    echo "Need to be executed as sudo"
    exit 1
fi

xhost +local:root # Allow root to connect to the X server

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
    #docker run -dt --privileged --name gnb ubuntu bash
    #docker run -dt --privileged --name gnb -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ubuntu bash
    #docker exec gnb apt update
    #docker exec gnb update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    #docker exec gnb apt install net-tools iproute2 iputils-ping ffmpeg tcpdump iptables python3-pip -y
    #docker exec gnb pip install ultralytics subprocess opencv-python -y
    docker run -dt --privileged --name gnb -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ubuntu bash
    docker exec gnb apt update
    docker exec gnb apt install software-properties-common -y
    docker exec gnb add-apt-repository ppa:deadsnakes/ppa -y
    docker exec gnb apt update
    docker exec gnb apt install python3.11 -y
    docker exec gnb update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    docker exec gnb apt install net-tools iproute2 iputils-ping ffmpeg htop tcpdump iptables python3-pip -y
    docker exec gnb pip install ultralytics opencv-python
    docker cp ../airsim/mediamtx/. gnb:.
    docker cp stream.py gnb:stream.py
    docker cp yolov8n.pt gnb:yolov8n.pt
    docker exec -d gnb ./mediamtx
    sleep 5 # Wait for mediamtx to start
    docker exec -d gnb python3 stream.py 
fi

