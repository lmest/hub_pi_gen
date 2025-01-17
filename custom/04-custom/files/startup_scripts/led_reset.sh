#!/bin/bash

echo 18 > /sys/class/gpio/unexport 
echo 18 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio18/direction
echo 1 > /sys/class/gpio/gpio18/value

sleep 0.2s

echo 24 > /sys/class/gpio/unexport
echo 24 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio24/direction
echo 0 > /sys/class/gpio/gpio24/value

sleep 0.2s

echo 12 > /sys/class/gpio/unexport
echo 12 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio12/direction
echo 0 > /sys/class/gpio/gpio12/value
    
