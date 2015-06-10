# Install dependencies
sudo apt-get update
sudo apt-get install build-essential
sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev wget
sudo apt-get install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

# Download OpenCV 2
cd /tmp
wget -O opencv2.zip https://github.com/Itseez/opencv/archive/2.4.11.zip
unzip opencv2.zip
cd openvc2
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE ..
make
sudo make install

# Download pip
pip install pip --upgrade
pip install -r requirements.txt

