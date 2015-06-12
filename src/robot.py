import argparse
import pickle
import time

import cv2
import numpy as np

import util


class Agent(object):
    def __init__(self):
        self.vc = None

    def open_eyes(self):
        if self.vc is not None:
            return False

        # Attempt to open eyes
        try:
            self.vc = cv2.VideoCapture(0)
        except:
            return False
        return self.vc.isOpened()

    def close_eyes(self):
        if self.vc is None:
            return False
        self.vc.release()
        self.vc = None

    def perceive(self, grayscale=True, crop=True, resize=(84, 84)):
        if self.vc is None:
            return None

        success, frame = self.vc.read()
        if not success:
            return None

        # Convert to gray color space
        if grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            assert len(frame.shape) == 2

        # Crop to be square
        if crop:
            min_dim = np.min(frame.shape)
            y_start, x_start = np.floor((frame.shape - min_dim) / 2)
            y_end, x_end = y_start + min_dim, x_start + min_dim
            frame = frame[y_start:y_end, x_start:x_end]
            assert frame.shape[0] == frame.shape[1]

        # Resize
        if resize is not None:
            frame = cv2.resize(frame, resize)
        return pickle.dumps(frame)  # Pyro4 does not support numpy

    def perform_action(self, action):
        # TODO: take physicial action
        print('performing action %d' % action)


def main(args):
    print('initializing agent "%s" ...' % args.name)
    agent = Agent()
    if not agent.open_eyes():
        exit('agent could not open eyes')

    # Read a frame to enable the web cam and give it some time to adjust to the lightning conditions
    if agent.perceive() is None:
        exit('agent could not open eyes')
    time.sleep(5.0)
    print('done!\n')

    print('running event loop ...')
    util.pyro_event_loop(args.name, agent)
    print('shutting down agent ...')
    agent.close_eyes()


def get_parser():
    parser = argparse.ArgumentParser(description='Server for nn-robot.')
    parser.add_argument('--name', help='name of the agent', default='nn-robot')
    return parser


if __name__ == '__main__':
    main(get_parser().parse_args())
