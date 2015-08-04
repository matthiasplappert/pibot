import logging

import Pyro4
import cv2
import numpy as np

import robot.actuators
import robot.sensors
from robot.actuators import MotorAction as Action


class GameEnvironment(object):
    def __init__(self, name, host=None, port=None):
        # Use pickle for serialization (because we serialize numpy arrays).
        Pyro4.config.SERIALIZER = 'pickle'

        # Connect to robot and configure it.
        uri = 'PYRONAME:' + name
        if host is not None:
            uri += '@' + str(host)
            if port is not None:
                uri += ':' + str(port)
        self.robot = Pyro4.Proxy(uri)
        self._configure_robot()

    def __enter__(self):
        if not self.robot.open():
            return None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.robot.close()

    def step(self, action):
        frame, reward, terminal, lives, _ = self.debug_step(action)
        return frame, reward, terminal, lives

    def debug_step(self, action):
        self._act(action)
        sensor_data = self.robot.perceive()
        frame, reward, terminal, lives = self._compute_new_state(action, sensor_data)
        return frame, reward, terminal, lives, sensor_data

    def reset(self):
        pass

    @property
    def actions(self):
        raise NotImplementedError()

    def _act(self, action):
        raise NotImplementedError()

    def _configure_robot(self):
        raise NotImplementedError()

    def _compute_new_state(self, action, sensor_data):
        raise NotImplementedError()


class ObstacleAvoidanceGameEnvironment(GameEnvironment):
    @property
    def actions(self):
        print('actions called')
        print self.robot.actuators
        return self.robot.actuators[0].actions

    def _act(self, action):
        actions = [action]
        self.robot.act(actions)

    def _configure_robot(self):
        # Configure Kinect.
        kinect = robot.sensors.KinectDepthCamera()
        kinect.resize = (84, 84)
        kinect.crop = True
        kinect.convert_color = None

        # Configure voltage sensor. We only need this information for debug reasons, so only query very infrequently.
        voltage = robot.sensors.VoltageSensor()
        voltage.step_interval = 1000

        # Configure motors
        motors = robot.actuators.SimulatedMotors()
        motors.action_duration = 0.05

        # Pass the configuration to the robot.
        self.robot.sensors = [kinect, voltage]
        self.robot.actuators = [motors]

    def _compute_new_state(self, action, sensor_data):
        depth_data = sensor_data[0]
        voltage = sensor_data[1]
        if voltage is not None:
            logging.info('system voltage is %fV' % voltage)

        # TODO: Calculate histogram and figure out if we are close to an obstacle
        is_too_close = False

        # We reward as follows:
        # - if the robot is too close to an obstacle, every action is punished
        # - if the robot is not too close to an obstacle AND performs a forward action, reward
        # - if the robot is not too close to an obstacle AND performs a non-forward action, do neither punish nor reward
        reward = 0
        if is_too_close:
            reward = -1
        elif action == Action.FORWARD:
            reward = 1

        # Prepare remaining values.
        frame = depth_data.astype('float32') / 4027.0
        terminal = False
        lives = 1 if not terminal else 0

        return frame, reward, terminal, lives

    def _compute_error_rate(self, depth_data):
        n_depth_errors = np.sum(depth_data == 4027)
        return float(n_depth_errors) / float(np.size(depth_data))

    def reset(self):
        while True:
            depth_data = self.robot.perceive()[0]
            error_rate = self._compute_error_rate(depth_data)
            if error_rate < 0.2:
                break
            self.robot.perform_action(Action.BACKWARD)


# class LightSeekingGameEnvironment(GameEnvironment):
#     def _compute_new_state(self, sensor_data):
#         assert len(sensor_data) >= 2
#         light = sensor_data[1]
#         if light > 80:
#             return 1
#         return 0
