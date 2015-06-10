# Install dependencies
sudo apt-get update
sudo apt-get install libopencv-dev python-opencv

# Download pip
source bin/activate
pip install pip --upgrade
pip install -r requirements.txt
ln -s /usr/lib/pymodules/python2.7/cv2.so lib/python2.7/cv2.so
