#!/usr/bin/env bash
RABBITMQ_URL=
RABBITMQ_USERNAME="admin"
RABBITMQ_PASSWORD="admin"
THREADS=1

echo export THREADS="${THREADS}" >> ~/.bashrc
source ~/.bashrc

sudo apt-get install -y git
git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-fedora-benchmark.git
ln -s vt-fedora-benchmark/utils/docker_collector.py collector.py

sudo apt-get update && apt-get install -y \
    curl \
    ntp
curl -fsSL https://get.docker.com/ | sh
sudo service ntp restart

for i in {1..${THREADS}}; do
    docker run -d --privileged --name=fedora_benchmark_${i} dedocibula/fedora-benchmark python experiment_coordinator.py ${RABBITMQ_URL} ${RABBITMQ_USERNAME} ${RABBITMQ_PASSWORD}
done