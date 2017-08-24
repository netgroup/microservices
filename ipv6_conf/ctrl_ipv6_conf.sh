#!/bin/bash

sudo ip -6 addr add fd3c:9f20:5d73:0b::01/64 dev ctr8-eth1

sudo sysctl -w net.ipv6.conf.all.forwarding=1

sudo ip -6 route add default via fd3c:9f20:5d73:0b::02 dev ctr8-eth1