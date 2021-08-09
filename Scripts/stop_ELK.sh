#!/usr/bin/env bash
cd /docker 
sudo docker stop docker_metricbeat_1
sudo docker stop elasticsearch
sudo docker stop kibana
sudo docker ps


