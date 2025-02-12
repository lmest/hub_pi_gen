#!/bin/bash

AMQP_CFG=/home/pi/scripts/amqp.configured

amqp_is_running()
{
    if systemctl is-active --quiet rabbitmq-server; then
        return 1
    else
        return 0
    fi
}

# if the file AMQP_CFG does not exist stop the server, 
# configure it and starts again
if [ ! -e "$AMQP_CFG" ]; then
    amqp_is_running
    if [ $? -eq 1 ]; then
        sudo systemctl disable rabbitmq-server
    fi
    sudo rabbitmqctl add_user smccedfw.petro UFE59BBAfQxPSqYvsYM755j74RzKuNjeGSKn3nGasyaibePe
    sudo rabbitmqctl set_user_tags smccedfw.petro administrator
    sudo rabbitmqctl set_permissions -p / smccedfw.petro ".*" ".*" ".*"
    sudo systemctl enable rabbitmq-server
    sudo rabbitmq-plugins enable rabbitmq_management

    touch "$AMQP_CFG" 
fi

   



