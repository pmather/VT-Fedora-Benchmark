#!/usr/bin/env bash
RABBITMQ_URL=rabbit-mq
RABBITMQ_USERNAME="admin"
RABBITMQ_PASSWORD="admin"
THREADS=1

echo export THREADS="${THREADS}" >> /etc/profile
source /etc/profile

sudo apt-get install -y git
git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-fedora-benchmark.git
ln -s vt-fedora-benchmark/orchestrators/docker_collector.py collector.py

sudo apt-get update && apt-get install -y \
    curl \
    ntp
curl -fsSL https://get.docker.com/ | sh
sudo service ntp restart

docker run -d -p 5672:5672 -p 15672:15672  --hostname ${RABBITMQ_URL} --name ${RABBITMQ_URL} -e RABBITMQ_DEFAULT_USER=${RABBITMQ_USERNAME} -e RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD} rabbitmq:management

for ((i = 1; i <= ${THREADS}; i++)) ; do
    docker run -d --privileged --link=${RABBITMQ_URL}:${RABBITMQ_URL} --name=fedora_benchmark_${i} dedocibula/fedora-benchmark python experiment_coordinator.py ${RABBITMQ_URL} ${RABBITMQ_USERNAME} ${RABBITMQ_PASSWORD}
done