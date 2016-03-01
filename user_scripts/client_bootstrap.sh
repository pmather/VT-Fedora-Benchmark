#!/bin/bash
sudo apt-get install git -y
git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-sil.git
vt-sil/utils/client_setup.sh

echo_supervisord_conf > /etc/supervisord.conf
echo "[program:rabbitmq_consumer]" >> /etc/supervisord.conf
echo "command=nice -n -5 python rabbitmq_consumer.py <rabbitmq_url> admin admin" >> /etc/supervisord.conf
echo "directory=${PWD}/vt-sil/experiments" >> /etc/supervisord.conf
echo "redirect_stderr=true" >> /etc/supervisord.conf
echo "stdout_logfile=${PWD}/vt-sil/experiments/experiment.out" >> /etc/supervisord.conf
echo "autostart=true" >> /etc/supervisord.conf
echo "autorestart=unexpected" >> /etc/supervisord.conf
supervisord