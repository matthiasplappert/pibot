import cv2
import Image

vc = cv2.VideoCapture(0)
if vc.isOpened():
    rval, frame = vc.read()
    im = Image.fromarray(frame)
    im.save('test.png')
