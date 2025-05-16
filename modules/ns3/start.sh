#!/bin/bash
#
# Copyright (c) 2023 Núcleo de P&D em Telecomunicações, Automação e Eletrônica (LASSE)
# Make sure you have docker installed on your system. 
#

if [[ $EUID -ne 0 ]];then
    echo "Need to be executed as sudo"
    exit 1
fi

# Creating both taps 
ip tuntap add tap-gnb mode tap

# Making both packet listeners, even if the mac dest address is not from the tap 
ip link set tap-gnb promisc on

# Upping both of tap's
ip link set tap-gnb up 

# Creating both bridges
ip link add name br-gnb type bridge

# Making both Tap's linked to the correct bridge
ip link set tap-gnb master br-gnb 

# Creating 'bridge rules"
sudo iptables -I FORWARD -m physdev --physdev-is-bridged -i br-gnb -p icmp -j ACCEPT
sudo iptables -I FORWARD -m physdev --physdev-is-bridged -i br-gnb -p tcp -j ACCEPT
sudo iptables -I FORWARD -m physdev --physdev-is-bridged -i br-gnb -p udp -j ACCEPT

PIDUE=$(docker inspect --format '{{ .State.Pid }}' ue)
PIDGNB=$(docker inspect --format '{{ .State.Pid }}' gnb)

#Create a new veth pair's to link the gnb container to the br-gnb
gNB="gnb"
ip link add eth-gnb type veth peer name eth
ip link set eth-gnb master br-gnb
ip link set eth-gnb up
ip link set eth netns $PIDGNB
docker exec $gNB ip addr add 10.1.2.2/24 dev eth 
docker exec $gNB ip link set eth up

#Route for coonectivity 
sudo docker exec -d $gNB ip route del default
sudo docker exec -d $gNB ip route add 10.1.1.0/24 via 10.1.2.1 dev eth

# Set bridges up
ip link set br-gnb up