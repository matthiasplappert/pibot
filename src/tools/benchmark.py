import argparse
import logging
import timeit
import random

import cv2

from util.frame_convert import pretty_depth_cv
from robot.base import get_remote_robot
from learner.games import ObstacleAvoidanceGameEnvironment


def main(args):
    print('preparing ...')
    robot = get_remote_robot(args.agent, args.host, args.port)
    with ObstacleAvoidanceGameEnvironment(robot) as game:
        if not game:
            print('could not create game')
            return
        actions = game.actions
        game.step(actions[0])  # perform a single step to ensure everything is set up before measuring

        n_iter = args.n_iter
        print('performing %d iterations ...' % n_iter)
        start = timeit.default_timer()
        for i in xrange(n_iter):
            frame, reward, terminal, lives = game.step(random.choice(actions))
            if terminal:
                print('resetting game ...')
                game.reset()
                continue
            #frame *= 2047.
            #cv2.cv.SaveImage('/Users/matze/Desktop/test/out_%.3d.png' % i, pretty_depth_cv(frame))
            #print reward, terminal

        duration = timeit.default_timer() - start
        fps = int(float(n_iter) / duration)
        print('total time: %fs (%dfps)' % (duration, fps))


def get_parser():
    parser = argparse.ArgumentParser(description='Benchmark for nn-robot.')
    parser.add_argument('--host', help='host of the robot, e.g. 192.168.1.2', type=str, default=None)
    parser.add_argument('--port', help='port of the robot, e.g. 9090', type=int, default=9090)
    parser.add_argument('--n-iter', help='number of iterations to perform', type=int, default=100)
    parser.add_argument('agent', help='name of the robot')
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(get_parser().parse_args())
