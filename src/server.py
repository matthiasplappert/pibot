import argparse
import logging
import timeit

import cv2

from util import Action
from game import GameEnvironment


def main(args):
    if args.debug_frames:
        cv2.namedWindow('debug-frames')

    prev_score = 0
    game = GameEnvironment(args.agent, host=args.host, port=args.port)
    while True:
        start = timeit.default_timer()
        frame, reward, terminal, lives = game.step(Action.IDLE)
        print('frame=%s, reward=%d, terminal=%d, lives=%d' % (str(frame.shape), reward, terminal, lives))

        if args.debug_frames:
            cv2.imshow('debug-frames', frame)
            cv2.waitKey(1)

        duration = timeit.default_timer() - start
        print('perceive-action cycle took %fs\n' % duration)

    if args.debug_frames:
        cv2.destroyWindow()


def get_parser():
    parser = argparse.ArgumentParser(description='Server for nn-robot.')
    parser.add_argument('--debug-frames', action='store_true', help='display each frame')
    parser.add_argument('--host', help='host of the robot, e.g. 192.168.1.2', type=str, default=None)
    parser.add_argument('--port', help='port of the robot, e.g. 9090', type=int, default=9090)
    parser.add_argument('agent', help='name of the agent')
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(get_parser().parse_args())
