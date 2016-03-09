#!/bin/bash
RABBITMQ_URL=
RABBITMQ_USERNAME="admin"
RABBITMQ_PASSWORD="admin"

git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-fedora-benchmark.git
vt-fedora-benchmark/utils/client_setup.sh
ln -s vt-fedora-benchmark/utils/vm_collector.py collector.py

echo_supervisord_conf > /etc/supervisord.conf
echo "[program:experiment_coordinator]" >> /etc/supervisord.conf
echo "command=nice -n -5 python experiment_coordinator.py ${RABBITMQ_URL} ${RABBITMQ_USERNAME} ${RABBITMQ_PASSWORD}" >> /etc/supervisord.conf
echo "directory=${PWD}/vt-fedora-benchmark/experiments" >> /etc/supervisord.conf
echo "redirect_stderr=true" >> /etc/supervisord.conf
echo "stdout_logfile=${PWD}/vt-fedora-benchmark/experiments/experiment.out" >> /etc/supervisord.conf
echo "autostart=true" >> /etc/supervisord.conf
echo "autorestart=unexpected" >> /etc/supervisord.conf
supervisord