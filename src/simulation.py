import argparse
import logging
import timeit
import random

import cv2

from game import GameEnvironment


def main(args):
    game = GameEnvironment(args.agent, host=args.host, port=args.port)
    cv2.namedWindow('frame')

    actions = game.get_actions()
    while True:
        action = random.choice(actions)
        frame, reward, terminal, lives = game.step(action)
        cv2.imshow('frame', frame)
        cv2.waitKey(1)

    cv2.destroyWindow('frame')


def get_parser():
    parser = argparse.ArgumentParser(description='Server for nn-robot.')
    parser.add_argument('--host', help='host of the robot, e.g. 192.168.1.2', type=str, default=None)
    parser.add_argument('--port', help='port of the robot, e.g. 9090', type=int, default=9090)
    parser.add_argument('agent', help='name of the agent')
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(get_parser().parse_args())
