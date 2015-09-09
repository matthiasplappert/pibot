import argparse
import logging

import numpy as np

from robot.base import get_remote_robot
from robot.sensors import *
from robot.actuators import *


def main(args):
    print('preparing ...')
    robot = get_remote_robot(args.agent, args.host, args.port)
    kinect_depth_cam = KinectDepthCamera()
    kinect_video_cam = KinectVideoCamera()
    kinect_tilt_sensor = KinectTiltSensor()
    kinect_tilt_motor = KinectTiltMotor()
    kinect_led = KinectLED()
    robot.sensors = [kinect_depth_cam, kinect_video_cam, kinect_tilt_sensor]
    robot.actuators = [kinect_tilt_motor, kinect_led]
    robot.open()

    print('switching LEDs ...')
    for action in kinect_led.actions:
        print '\t' + str(action)
        robot.act([None, action])
        time.sleep(1)

    print('\nmoving tilt motor ...')
    print('\t+20 degrees')
    robot.act([20, None])
    time.sleep(3)
    print('\t-20 degrees')
    robot.act([-20, None])
    time.sleep(3)
    print('\t  0 degrees')
    robot.act([0, None])
    time.sleep(3)

    print('\nreading tilt status ...')
    for _ in xrange(10):
        print '\t' + str(robot.perceive()[2])
        time.sleep(1)

    print('\nreading depth frames ...')
    for _ in xrange(10):
        print '\t' + str(np.mean(robot.perceive()[0]))
        time.sleep(1)

    print('\nreading video frames ...')
    for _ in xrange(10):
        print '\t' + str(np.mean(robot.perceive()[1]))
        time.sleep(1)

    robot.close()


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
