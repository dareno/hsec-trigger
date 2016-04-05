Description
-----------
Home security project. Raspberry Pi using MCP23017 and GPIO with interrupts.

The vision is to have a microservice architecture, home security system with no service fees. Maybe not super practical, but a fun exercise. Also, super-useful when done. 

The Hardware (humble beginnings...)
-----------------------------------
<img src="https://github.com/dareno/hsec/blob/master/img/hardware.jpg" alt="Raspberry Pi with MCP21017" width="153">

Technology
----------
* Raspberry Pi because it's small, low power, and runs linux so I don't have to re-invent the wheel on a microcontroller.
* Python for Raspberry Pi stuff because it's common in the ecosystem
* Python3 because it's new
* MCP23017 because it's a cheap port expander and there are examples
* i2c bus for IC to IC communication because there are examples
* smbus standard over i2c because there are examples
* RPi.GPIO because I can use it to process interrupts on the MCP23017
* zmq because I don't need a broker process making this lighter weight for a RPi. 

Architecture
------------
* hsec-trigger.py - look for events on the hardware and share them
* hsec-state.py - receive events, update and share state
* hsec-alert.py - listen for state changes, alert. (e.g. call my phone)
* commchannel.py - encapsulate messaging technology (e.g. ZeroMQ)
* MCP23017.py - encapsulate i2c/smbus IC commands 


To Do
-----
* update main loop to use a distinct thread per device (only 1 device/MCP today)
* iPhone app to add reporting and state events (e.g. arm motion detectors, arm windows, arm doors)

How To Use
----------
```
#download raspbian minimal to your laptop and write image to sd card : 
https://www.raspberrypi.org/downloads/raspbian/
# sudo dd bs=1m if=path_of_your_image.img of=/dev/rdisk2 # DON'T COPY/PASTE, VERIFY TARGET DISK

# boot, able to ssh straight to RPi
# ssh pi@192.168.1.165 # check your router for IP address

# enlarge file system and enable i2c
sudo raspi-config

# ssh from pi to pi to create .ssh
ssh localhost

# setup passwordless login
scp /Users/david/.ssh/id_rsa.pub pi@192.168.1.165:/home/pi/.ssh/authorized_keys

# add set -o vi to end of profile
sudo vi /etc/profile 

# update raspbian
sudo apt-get -y update && sudo apt-get -y upgrade

# install screen
sudo apt-get install -y screen

# docker
sudo wget https://downloads.hypriot.com/docker-hypriot_1.10.3-1_armhf.deb
sudo dpkg -i docker-hypriot_1.10.3-1_armhf.deb
#sudo docker run armhf/debian /bin/echo 'Hello World'

# don't need this, just for troubleshooting...
# sudo apt-get -y install build-essential libi2c-dev i2c-tools python-dev libffi-dev module-init-tools

# done with Raspbian configuration, now launch the container and configure

# run a shell
# thanks dummdida... http://dummdida.tumblr.com/post/117157045170/modprobe-in-a-docker-container
sudo docker run --name hsec-container --privileged --cap-add=ALL -it -v /dev:/dev -v /lib/modules:/lib/modules armhf/debian /bin/bash

set -o vi
ls -la /dev/i2c-1 # verify the special file exists...
apt-get -y update && apt-get -y install vim python3 python3-pip python3-zmq git build-essential libi2c-dev i2c-tools python-dev libffi-dev
pip3 install RPi.GPIO cffi smbus-cffi

# optional, verify RPi.GPIO
# python3
#>>> import sys
#>>> sys.path.append("/usr/local/lib/python3.4/dist-packages/")
#>>> import RPi.GPIO as GPIO
#>>> 

# install the hsec code
cd
git clone https://github.com/dareno/hsec-trigger.git
cd hsec-trigger/hsec-trigger/
git clone https://github.com/dareno/comms.git
cd
git clone https://github.com/dareno/hsec-state.git
cd hsec-state/hsec-state/
git clone https://github.com/dareno/comms.git
cd
git clone https://github.com/dareno/hsec-alert.git
cd hsec-alert/hsec-alert/
git clone https://github.com/dareno/comms.git
cp hsec-alert-example.cfg hsec-alert.cfg

# put ifttt.com make channel password into config file
vi hsec-alert.cfg

# run the hsec code
~/hsec-alert/hsec-alert/hsec-alert.py &
~/hsec-state/hsec-state/hsec-state.py &
~/hsec-trigger/hsec-trigger/hsec-trigger.py &
```

