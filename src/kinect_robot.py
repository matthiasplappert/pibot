import argparse
import logging
import time

import cv2
import numpy as np
import Pyro4
import freenect

# Attempt to load gopigo, which is not available everywhere
gopigo_available = True
try:
    import gopigo
except ImportError:
    gopigo_available = False

from util import pyro_event_loop, Action


class Agent(object):
    def __init__(self):
        self.counts = np.zeros(len(self.get_actions()))
        self.episode_counts = np.zeros(len(self.get_actions()))
        self.steps = 0

    def get_actions(self):
        return [Action.FORWARD, Action.BACKWARD, Action.IDLE, Action.TURN_LEFT, Action.TURN_RIGHT]

    def open_eyes(self):
        return True

    def close_eyes(self):
        return True

    def sense_light(self):
        if not gopigo_available:
            logging.info('simulating sense_light')
            return 0
        value = gopigo.analogRead(1)
        return value

    def perceive(self, grayscale=True, crop=True, resize=(100, 100)):
        frame, _ = freenect.sync_get_depth()
        
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
        self.counts[action] += 1
        self.episode_counts[action] += 1
        self.steps += 1
        if self.steps % 100 == 0:
            volt = -1.0
            if gopigo_available:
                volt = gopigo.volt()
            logging.info('performed %d steps\t%s\t%s\t%fV' % (self.steps, self.episode_counts, self.counts, volt))
            self.episode_counts[:] = 0

        if not gopigo_available:
            logging.info('simulating action %d' % action)
            time.sleep(duration)
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
    pyro_event_loop(args.name, agent, host=args.host, port=args.port)
    print('shutting down agent ...')
    agent.close_eyes()


def get_parser():
    parser = argparse.ArgumentParser(description='Server for nn-robot.')
    parser.add_argument('--name', help='name of the agent', default='nn-robot')
    parser.add_argument('--port', help='port of the name server', default=9090, type=int)
    parser.add_argument('--host', help='host of the name server', default=None, type=str)
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if not gopigo_available:
        logging.warning('gopigo library not available, resorting to simulation')
    main(get_parser().parse_args())
