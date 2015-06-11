import argparse
import pickle
import timeit

import cv2
import Pyro4
import numpy as np

import actions


def main(args):
    vc = cv2.VideoCapture(0)
    if not vc.isOpened():
        print('cannot open video capture session')
        exit()

    uri = args.uri
    agent = Pyro4.Proxy(uri)
    config = agent.client_config()
    print('client config: %s' % config)
    print('running client ...\n')

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

        # TODO: should this be scaled to [0,1]?

        action = agent.perceive(pickle.dumps(frame))
        print('performing action %d' % action)

        duration = timeit.default_timer() - start
        print('perceive-action cycle took %fs\n' % duration)
        if action == actions.ABORT:
            break
        # TODO: perform physical action

    print('client shutting down ...')
    vc.release()


def get_parser():
    parser = argparse.ArgumentParser(description='Client control for nn-robot.')
    parser.add_argument('uri', help='the URI for Pyro4 of form PYRO:<obj>@<host>:<port>')
    return parser


if __name__ == '__main__':
    main(get_parser().parse_args())
