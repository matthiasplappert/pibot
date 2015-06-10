brew install update
brew install homebrew/science/opencv

virtualenv ./
source bin/activate
pip install pip --upgrade
pip install -r requirements.txt
ln -s /usr/local/lib/python2.7/site-packages/cv2.so lib/python2.7/cv2.so

