import argparse
import logging

from robot.base import run_robot
import robot.sensors


SENSORS = {'kinect-depth': robot.sensors.KinectDepthCamera,
           'kinect-rgb': robot.sensors.KinectCamera,
           'webcam': robot.sensors.OpenCVCamera,
           'voltage': robot.sensors.VoltageSensor,
           'analog': robot.sensors.AnalogSensor}


def main(args):
    sensors = []
    for s in args.sensors:
        sensors.append(SENSORS[s]())
    run_robot(sensors, args.name, args.host, args.port)


def get_parser():
    parser = argparse.ArgumentParser(description='Run nn-robot.')
    parser.add_argument('--name', help='name of the robot', default='nn-robot')
    parser.add_argument('--port', help='port of the robot on the network', default=9090, type=int)
    parser.add_argument('--host', help='host of the robot on the network', default=None, type=str)
    parser.add_argument('sensors', help='sensors of the robot', choices=SENSORS.keys(), nargs='+')
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(get_parser().parse_args())
