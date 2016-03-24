#!/bin/bash
RABBITMQ_URL=
RABBITMQ_USERNAME="admin"
RABBITMQ_PASSWORD="admin"
THREADS=1

echo export THREADS="${THREADS}" >> /etc/profile
source /etc/profile

sudo apt-get install -y git
git clone https://DedoCibula@bitbucket.org/DedoCibula/vt-fedora-benchmark.git
vt-fedora-benchmark/utils/client_setup.sh
ln -s vt-fedora-benchmark/utils/vm_collector.py collector.py

echo_supervisord_conf > /etc/supervisord.conf
for ((i = 1; i <= ${THREADS}; i++)) ; do
    mkdir ${PWD}/vt-fedora-benchmark/${i}
    cp -R ${PWD}/vt-fedora-benchmark/experiments/* ${PWD}/vt-fedora-benchmark/${i}

    echo "[program:experiment_coordinator_${i}]" >> /etc/supervisord.conf
    echo "command=nice -n -5 python experiment_coordinator.py ${RABBITMQ_URL} ${RABBITMQ_USERNAME} ${RABBITMQ_PASSWORD}" >> /etc/supervisord.conf
    echo "directory=${PWD}/vt-fedora-benchmark/${i}" >> /etc/supervisord.conf
    echo "redirect_stderr=true" >> /etc/supervisord.conf
    echo "stdout_logfile=${PWD}/vt-fedora-benchmark/${i}/experiment${i}.out" >> /etc/supervisord.conf
    echo "autostart=true" >> /etc/supervisord.conf
    echo "autorestart=unexpected" >> /etc/supervisord.conf
done

supervisord