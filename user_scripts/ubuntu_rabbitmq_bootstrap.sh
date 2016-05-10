#!/bin/bash
RABBITMQ_USERNAME="admin"
RABBITMQ_PASSWORD="admin"

wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
sudo apt-key add rabbitmq-signing-key-public.asc
sudo apt-get upgrade && supo apt-get update
sudo apt-get install rabbitmq-server -y
sudo service rabbitmq-server start
sudo rabbitmq-plugins enable rabbitmq_management
sudo rabbitmqctl add_user ${RABBITMQ_USERNAME} ${RABBITMQ_PASSWORD}
sudo rabbitmqctl set_user_tags ${RABBITMQ_USERNAME} administrator
sudo rabbitmqctl set_permissions -p / ${RABBITMQ_USERNAME} ".*" ".*" ".*"
sudo rabbitmqctl delete_user guest
sudo service rabbitmq-server restart
rm rabbitmq-signing-key-public.asc