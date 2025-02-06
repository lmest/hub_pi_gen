#!/bin/bash

if [ ! -d /run/screen ]; then
    sudo mkdir -p /run/screen
fi

sudo chmod 777 /run/screen

/usr/bin/python3 /home/pi/server/watchdog.py
