#!/bin/bash
#
# Copyright (c) 2023 Núcleo de P&D em Telecomunicações, Automação e Eletrônica (LASSE)
# Make sure you have docker installed on your system. 
#

if [[ $EUID -ne 0 ]];then
    echo "Need to be executed as sudo"
    exit 1
fi

ip link add eth-client type veth peer name eth-server

PID_CLIENT=$(docker inspect --format '{{ .State.Pid }}' caviar.grafana)
PID_SERVER=$(docker inspect --format '{{ .State.Pid }}' gnb)

ip link set eth-client netns $PID_CLIENT
ip link set eth-server netns $PID_SERVER

docker exec caviar.grafana ip addr add 192.168.1.1/24 dev eth-client
docker exec caviar.grafana ip link set eth-client up

docker exec gnb ip addr add 192.168.1.2/24 dev eth-server
docker exec gnb ip link set eth-server up

docker exec caviar.grafana ip route add 192.168.1.0/24 dev eth-client
docker exec gnb ip route add 192.168.1.0/24 dev eth-server