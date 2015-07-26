# Raspberry Pi Installation

## Basics
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential git
```
Next, generate keys for Github: https://help.github.com/articles/generating-ssh-keys/

## nn-robot and Dependencies
```
sudo apt-get install python python-dev python-numpy python-scipy python-setuptools libopencv-dev python-opencv
git clone git@github.com:matthiasplappert/nn-robot.git ~/nn-robot
cd ~/nn-robot
git submodule update --init --recursive
sudo pip install pip --upgrade
sudo pip install -r requirements.txt
```

## GoPiGo
```
cd vendor/gopigo/Setup
chmod +x install.sh
sudo ./install.sh
```

## Xbox Kinect
```
cd /tmp
sudo apt-get install libudev-dev
sudo wget http://sourceforge.net/projects/libusb/files/libusb-1.0/libusb-1.0.19/libusb-1.0.19.tar.bz2/download
tar xvjf download
cd libusb-1.0.19
./configure
make
sudo make install
cd ~/nn-robot/vendor/libfreenect
sudo apt-get install cmake freeglut3-dev libxmu-dev libxi-dev
mkdir build
cmake -DBUILD_EXAMPLES=OFF -DLIBUSB_1_INCLUDE_DIR=/usr/local/include/libusb-1.0 -DLIBUSB_1_LIBRARY=/usr/local/lib/libusb-1.0.so -L ..
make
sudo make install
cd ../wrappers/python
sudo python setup.py install
```

TODO: Describe udev rule stuff

## WiFi
TODO
