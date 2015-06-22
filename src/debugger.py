import argparse
import logging
import timeit
import time
import curses

import cv2

from util import Action
from game import GameEnvironment


def main(args):
    game = GameEnvironment(args.agent, host=args.host, port=args.port)

    # Window for frame
    cv2.namedWindow('frame')
    cv2.namedWindow('processed-frame')

    # Interactive terminal
    stdscr = curses.initscr()
    stdscr.keypad(True)
    curses.halfdelay(1)
    while True:
        try:
            key = stdscr.getkey()
        except:
            key = ''

        if key == 'KEY_UP':
            action = Action.FORWARD
        elif key == 'KEY_DOWN':
            action = Action.BACKWARD
        elif key == 'KEY_LEFT':
            action = Action.TURN_LEFT
        elif key == 'KEY_RIGHT':
            action = Action.TURN_RIGHT
        elif key.upper() == 'X':
            break
        else:
            action = Action.IDLE

        start = timeit.default_timer()
        frame, reward, terminal, lives, processed_frame = game.debug_step(action)
        duration = timeit.default_timer() - start

        stdscr.clear()
        stdscr.addstr(0, 0, 'action: %d' % action)
        stdscr.addstr(1, 0, 'frame: %s' % str(frame.shape))
        stdscr.addstr(2, 0, 'reward: %d' % reward)
        stdscr.addstr(3, 0, 'terminal: %s' % terminal)
        stdscr.addstr(4, 0, 'lives: %d' % lives)
        stdscr.addstr(4, 0, 'perceive-action cycle duration: %fs' % duration)
        stdscr.refresh()

        cv2.imshow('frame', frame)
        cv2.imshow('processed-frame', processed_frame)
        cv2.waitKey(1)
        if args.interval > 0: time.sleep(args.interval)

    # Tear down frame
    cv2.destroyWindow('frame')
    cv2.destroyWindow('processed-frame')


def get_parser():
    parser = argparse.ArgumentParser(description='Server for nn-robot.')
    parser.add_argument('--host', help='host of the robot, e.g. 192.168.1.2', type=str, default=None)
    parser.add_argument('--port', help='port of the robot, e.g. 9090', type=int, default=9090)
    parser.add_argument('--interval', help='update interval in seconds', type=int, default=0)
    parser.add_argument('agent', help='name of the agent')
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(get_parser().parse_args())
