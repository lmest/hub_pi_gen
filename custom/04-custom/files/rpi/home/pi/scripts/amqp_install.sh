#!/bin/bash

if systemctl is-active --quiet rabbitmq-server; then
    sudo systemctl disable rabbitmq-server
fi

sudo rabbitmqctl add_user smccedfw.petro UFE59BBAfQxPSqYvsYM755j74RzKuNjeGSKn3nGasyaibePe
sudo rabbitmqctl set_user_tags smccedfw.petro administrator
sudo rabbitmqctl set_permissions -p / smccedfw.petro ".*" ".*" ".*"
sudo systemctl enable rabbitmq-server
sudo rabbitmq-plugins enable rabbitmq_management
