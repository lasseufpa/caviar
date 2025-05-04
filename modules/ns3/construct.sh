#!/bin/bash
#
# Copyright (c) 2023 Núcleo de P&D em Telecomunicações, Automação e Eletrônica (LASSE)
# 
#
# Make sure you have docker installed on your system. 
# If you are using ubuntu 22.04, do:
#

if [[ $EUID -ne 0 ]];then
    echo "Need to be executed as sudo"
    exit 1
fi

docker run -dt --privileged --name ue ubuntu bash
docker run -dt --privileged --name gnb ubuntu bash
docker start ue gnb

docker exec ue apt update 
docker exec ue apt install net-tools iproute2 iputils-ping -y 
docker exec gnb apt update 
docker exec gnb apt install net-tools iproute2 iputils-ping -y 
