import argparse
import logging

import numpy as np

from robot.base import get_remote_robot
from robot.sensors import *
from robot.actuators import *


def main(args):
    print('preparing ...')
    robot = get_remote_robot(args.agent, args.host, args.port)
    motors = Motors()
    motors.speed = 50
    robot.sensors = [VoltageSensor()]
    robot.actuators = [motors]
    robot.open()

    # Read the sensor value, which is the voltage.
    print(robot.perceive())

    # Drive the motor in different modes.
    robot.act([MotorAction.FORWARD])
    time.sleep(1)
    robot.act([MotorAction.TURN_LEFT])
    time.sleep(1)
    robot.act([MotorAction.TURN_RIGHT])
    time.sleep(1)
    robot.act([MotorAction.IDLE])
    time.sleep(1)

    robot.close()


def get_parser():
    parser = argparse.ArgumentParser(description='Benchmark for PiBot.')
    parser.add_argument('--host', help='host of the robot, e.g. 192.168.1.2', type=str, default=None)
    parser.add_argument('--port', help='port of the robot, e.g. 9090', type=int, default=9090)
    parser.add_argument('agent', help='name of the robot')
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(get_parser().parse_args())
