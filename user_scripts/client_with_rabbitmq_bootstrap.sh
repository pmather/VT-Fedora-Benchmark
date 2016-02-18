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