#!/usr/bin/env bash
cd /docker 
sudo docker stop elasticsearch
sudo docker stop metricbeat
sudo docker stop heartbeat
sudo docker stop kibana
sudo docker ps


