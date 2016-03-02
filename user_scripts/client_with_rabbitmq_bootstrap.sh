#!/bin/bash
wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
sudo apt-key add rabbitmq-signing-key-public.asc
sudo apt-get update
sudo apt-get install rabbitmq-server -y
sudo service rabbitmq-server start
sudo rabbitmq-plugins enable rabbitmq_management
sudo rabbitmqctl add_user admin admin
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
sudo rabbitmqctl delete_user guest
sudo service rabbitmq-server restart
rm rabbitmq-signing-key-public.asc

sudo apt-get install git -y
git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-sil.git
vt-sil/utils/client_setup.sh

echo_supervisord_conf > /etc/supervisord.conf
echo "[program:rabbitmq_consumer]" >> /etc/supervisord.conf
echo "command=nice -n -5 python experiment_coordinator.py localhost admin admin" >> /etc/supervisord.conf
echo "directory=${PWD}/vt-sil/experiments" >> /etc/supervisord.conf
echo "redirect_stderr=true" >> /etc/supervisord.conf
echo "stdout_logfile=${PWD}/vt-sil/experiments/experiment.out" >> /etc/supervisord.conf
echo "autostart=true" >> /etc/supervisord.conf
echo "autorestart=unexpected" >> /etc/supervisord.conf
supervisord