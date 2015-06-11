import pickle
import timeit

import cv2
import Pyro4
import numpy as np

import actions


def main():
    # Connect to server, which runs our agent (for performance reasons only)
    agent = Pyro4.Proxy('PYRONAME:agent')
    config = agent.config()
    print('client config: %s' % config)

    # Open eyes
    vc = cv2.VideoCapture(0)
    if not vc.isOpened():
        exit('cannot open video capture session')

    print('running agent ...\n')
    while True:
        start = timeit.default_timer()
        success, frame = vc.read()
        if not success:
            print('could not read from video capture session')
            continue

        # Convert to gray color space
        if config['image_gray']:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            min_dim = np.min(frame.shape)
            assert len(frame.shape) == 2

        # Crop to be square
        if config['image_crop']:
            y_start, x_start = np.floor((frame.shape - min_dim) / 2)
            y_end, x_end = y_start + min_dim, x_start + min_dim
            frame = frame[y_start:y_end, x_start:x_end]
            assert frame.shape[0] == frame.shape[1]

        # Scale down
        if config['image_resize'] is not None:
            frame = cv2.resize(frame, config['image_resize'])

        action = agent.perceive(pickle.dumps(frame))
        print('performing action %d' % action)

        duration = timeit.default_timer() - start
        print('perceive-action cycle took %fs\n' % duration)
        if action == actions.ABORT:
            break
        # TODO: perform physical action

    print('agent shutting down ...')
    vc.release()


if __name__ == '__main__':
    main()
