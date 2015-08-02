import argparse
import logging
import timeit
import random

from game import GameEnvironment


def main(args):
    print('preparing ...')
    game = GameEnvironment(args.agent, args.host, args.port)
    actions = game.get_actions()
    game.step(actions[0])  # perform a single step to ensure everything is set up before measuring

    n_iter = args.n_iter
    print('performing %d iterations ...' % n_iter)
    start = timeit.default_timer()
    for _ in xrange(n_iter):
        game.step(random.choice(actions))
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
