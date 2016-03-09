#!/usr/bin/env bash
RABBITMQ_URL=
RABBITMQ_USERNAME="admin"
RABBITMQ_PASSWORD="admin"

git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-fedora-benchmark.git
ln -s vt-fedora-benchmark/utils/docker_collector.py collector.py

curl -fsSL https://get.docker.com/ | sh

docker run -d -p 5672:5672 -p 15672:15672  --hostname rabbit-mq --name rabbit-mq -e RABBITMQ_DEFAULT_USER=${RABBITMQ_USERNAME} -e RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD} rabbitmq:management

docker run -d --privileged --name=fedora_benchmark dedocibula/fedora-benchmark python experiment_coordinator.py ${RABBITMQ_URL} ${RABBITMQ_USERNAME} ${RABBITMQ_PASSWORD}