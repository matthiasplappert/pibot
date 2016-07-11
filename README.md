# PiBot

![pibot](/assets/pibot.jpg?raw=true)
A simple robot platform with extensible sensors written in Python and controllable over Wifi.

## Hardware
- [Raspberry Pi 2](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/). You can probably use the newer [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) as well, but I haven't tried it.
- [GoPiGo](http://www.dexterindustries.com/gopigo/), which turns your Raspberry Pi into a basic robot platform.
- [Xbox 360 Kinect](http://www.xbox.com/en-US/xbox-360/accessories/kinect), if you want depth information. Alternatively, you can use any OpenCV-compatible (= most) USB web cam for vision.
- [A decent USB Wifi dongle](https://www.amazon.de/gp/product/B007K871ES/ref=oh_aui_search_detailpage?ie=UTF8&psc=1). I wouldn't get one of the tiny ones since I had bandwidth trouble, presumably due to the tiny antenna.
- A 3D printed holder for the Xbox Kinect. You can use my model (under `assets/kinect_gopigo.stl`), if you want. It contains holes so that you can easily attach it to your GoPiGo body. Alternatively, you can just attach it using tape or whatever.
- A battery pack of your choice. I use 10 AA rechargeable batteries since the Kinect requires at least 12V or it will just randomly shut down during operation, especially if the motors are also running. I use eneloop batteries, which are awesome. I get approx. 2 hours of a set of fully charged batteries.
- Some soldering equipment and patience to put it all together.

## Installation

### Basics
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential git
```
Next, generate keys for Github: https://help.github.com/articles/generating-ssh-keys/

### PiBot and Dependencies
```
sudo apt-get install python python-dev python-numpy python-scipy python-setuptools libopencv-dev python-opencv
git clone git@github.com:matthiasplappert/pibot.git ~/pibot
cd ~/pibot
git submodule update --init --recursive
sudo pip install pip --upgrade
sudo pip install -r requirements.txt
```

### GoPiGo
```
cd vendor/gopigo/Setup
chmod +x install.sh
sudo ./install.sh
```

### Xbox Kinect
```
cd /tmp
sudo apt-get install libudev-dev
sudo wget http://sourceforge.net/projects/libusb/files/libusb-1.0/libusb-1.0.19/libusb-1.0.19.tar.bz2/download
tar xvjf download
cd libusb-1.0.19
./configure
make
sudo make install
cd ~/pibot/vendor/libfreenect
sudo apt-get install cmake freeglut3-dev libxmu-dev libxi-dev
mkdir build
cmake -DBUILD_EXAMPLES=OFF -DLIBUSB_1_INCLUDE_DIR=/usr/local/include/libusb-1.0 -DLIBUSB_1_LIBRARY=/usr/local/lib/libusb-1.0.so -L ..
make
sudo make install
cd ../wrappers/python
sudo python setup.py install
```

TODO: Describe udev rule stuff

### WiFi
TODO
