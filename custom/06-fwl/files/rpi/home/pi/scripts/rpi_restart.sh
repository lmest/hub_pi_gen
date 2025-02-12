#!/bin/bash

port="/dev/ttyUSB2"

# Check and kill any process using this serial
proc_id=$(lsof $port | awk 'NR>1 {print $2}')

if [ -n "$proc_id" ]; then
    kill -9 $proc_id
fi

sleep 1
echo "AT+CFUN=4,0\r" > $port 
sleep 1

sudo shutdown -r now
