#!/bin/bash
sudo apt-get install git -y
git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-sil.git
vt-sil/utils/client_setup.sh
python vt-sil/experiments/rabbitmq_consumer.py <rabbitmq_endpoint> admin admin