#!/usr/bin/env bash
RABBITMQ_URL=
RABBITMQ_USERNAME="admin"
RABBITMQ_PASSWORD="admin"

sudo apt-get install -y git
git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-fedora-benchmark.git
ln -s vt-fedora-benchmark/utils/docker_collector.py collector.py

curl -fsSL https://get.docker.com/ | sh

docker run -d --privileged --name=fedora_benchmark dedocibula/fedora-benchmark python experiment_coordinator.py ${RABBITMQ_URL} ${RABBITMQ_USERNAME} ${RABBITMQ_PASSWORD}