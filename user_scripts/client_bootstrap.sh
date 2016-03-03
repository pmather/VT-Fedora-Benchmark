#!/bin/bash
sudo apt-get install git -y
git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-fedora-benchmark.git
vt-fedora-benchmark/utils/client_setup.sh

echo_supervisord_conf > /etc/supervisord.conf
echo "[program:experiment_coordinator]" >> /etc/supervisord.conf
echo "command=nice -n -5 python experiment_coordinator.py <rabbitmq_url> admin admin" >> /etc/supervisord.conf
echo "directory=${PWD}/vt-fedora-benchmark/experiments" >> /etc/supervisord.conf
echo "redirect_stderr=true" >> /etc/supervisord.conf
echo "stdout_logfile=${PWD}/vt-fedora-benchmark/experiments/experiment.out" >> /etc/supervisord.conf
echo "autostart=true" >> /etc/supervisord.conf
echo "autorestart=unexpected" >> /etc/supervisord.conf
supervisord