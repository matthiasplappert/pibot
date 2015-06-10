import pickle

import cv2
import Pyro4
import numpy as np


def main():
	vc = cv2.VideoCapture(0)
	if not vc.isOpened():
		print('cannot open video capture session')
		exit()

	uri = 'PYRO:obj_0855fae648b54026adb872b6ae3fc970@localhost:60359'
	agent = Pyro4.Proxy(uri)
	while True:
		succ, frame = vc.read()
		if not succ:
			print('could not read from video capture session')
			continue

		# Convert to gray color space
		frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
		min_dim = np.min(frame.shape)
		assert len(frame.shape) == 2

		# Crop to be square
		y_start, x_start = (frame.shape - min_dim) / 2
		y_end = y_start + min_dim
		x_end = x_start + min_dim
		frame = frame[y_start:y_end, x_start:x_end]
		assert frame.shape[0] == frame.shape[1]

		# Scale down
		frame = cv2.resize(frame, (84, 84))

		action = agent.perceive(pickle.dumps(frame))
		print('performing action %s' % action)
		# TODO: perform physical action


if __name__ == '__main__':
	main()
