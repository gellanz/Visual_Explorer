#!/usr/bin/env bash
cd /docker 
sudo sysctl -w vm.max_map_count=262144
sudo docker start elasticsearch
sudo docker start kibana
sudo docker start metricbeat
sudo docker start heartbeat
sudo docker ps

