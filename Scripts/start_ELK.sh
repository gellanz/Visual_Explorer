#!/usr/bin/env bash
cd /docker 
sudo sysctl -w vm.max_map_count=262144
sudo docker start elasticsearch
sudo docker start kibana
sudo docker ps
sudo service metricbeat start
sudo service heartbeat-elastic start

