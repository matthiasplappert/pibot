import argparse
import pickle
import time

import cv2
import numpy as np

from util import pyro_event_loop, Action


class Agent(object):
    def __init__(self):
        self.vc = None

    @property
    def get_actions(self):
        return [Action.FORWARD, Action.BACKWARD, Action.IDLE, Action.TURN_LEFT, Action.TURN_RIGHT]

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

    def perceive(self, grayscale=True, crop=True, resize=(100, 100)):
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
    if not agent.open_eyes() or agent.perceive() is None:
        exit('agent could not open eyes')
    print('done!\n')

    print('Pyro4 name server is listening on port %d' % args.port)
    print('starting event loop ...')
    pyro_event_loop(args.name, agent, ns_port=args.port)
    print('shutting down agent ...')
    agent.close_eyes()


def get_parser():
    parser = argparse.ArgumentParser(description='Server for nn-robot.')
    parser.add_argument('--name', help='name of the agent', default='nn-robot')
    parser.add_argument('--port', help='port of the name server', default=9090, type=int)
    return parser


if __name__ == '__main__':
    main(get_parser().parse_args())
