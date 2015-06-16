import argparse
import logging
import time

import cv2
import numpy as np
import Pyro4

# Attempt to load gopigo, which is not available everywhere
gopigo_available = True
try:
    import gopigo
except ImportError:
    gopigo_available = False

from util import pyro_event_loop, Action


class Agent(object):
    def __init__(self):
        self.vc = None

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
        return frame

    def perform_action(self, action, duration=0.1):
        if not gopigo_available:
            logging.info('simulating action %d' % action)
            return
        logging.info('performing action %d' % action)

        # Translate to action
        if action == Action.TURN_LEFT:
            action_call = gopigo.left
        elif action == Action.TURN_RIGHT:
            action_call = gopigo.right
        elif action == Action.FORWARD:
            action_call = gopigo.fwd
        elif action == Action.BACKWARD:
            action_call = gopigo.bwd
        elif action == Action.IDLE:
            action_call = gopigo.stop
        else:
            action_call = None
        if action_call is None:
            raise ValueError('unknown action %d' % action)

        # Perform action for `duration` seconds and stop afterwards
        action_call()
        time.sleep(duration)
        gopigo.stop()


def main(args):
    print('initializing agent "%s" ...' % args.name)
    agent = Agent()
    if not agent.open_eyes() or agent.perceive() is None:
        exit('agent could not open eyes')
    print('done!\n')

    Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

    print('starting event loop ...')
    pyro_event_loop(args.name, agent, ip=args.ip, port=args.port)
    print('shutting down agent ...')
    agent.close_eyes()


def get_parser():
    parser = argparse.ArgumentParser(description='Server for nn-robot.')
    parser.add_argument('--name', help='name of the agent', default='nn-robot')
    parser.add_argument('--port', help='port of the name server', default=9090, type=int)
    parser.add_argument('--ip', help='ip of the name server', default=None, type=str)
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if not gopigo_available:
        logging.warning('gopigo library not available, resorting to simulation')
    main(get_parser().parse_args())
