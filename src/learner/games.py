import logging

import numpy as np

from robot.sensors import KinectDepthCamera, KINECT_INVALID_DEPTH, VoltageSensor
from robot.actuators import Motors, SimulatedMotors, MotorAction, KinectTiltMotor, KinectLED, KinectLEDAction


class GameEnvironment(object):
    def __init__(self, r):
        self.robot = r
        self._configure_robot()

    def __enter__(self):
        if not self.robot.open():
            return None
        self._prepare_robot()
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

    def _prepare_robot(self):
        pass

    def _compute_new_state(self, action, sensor_data):
        raise NotImplementedError()


class ObstacleAvoidanceGameEnvironment(GameEnvironment):
    @property
    def actions(self):
        return self.robot.actuators[0].actions

    def _act(self, action):
        actions = [action, None, None]
        self.robot.act(actions)

    def _configure_robot(self):
        # Configure Kinect.
        kinect = KinectDepthCamera()
        kinect.resize = (84, 84)
        kinect.crop = True
        kinect.convert_color = None

        # Configure voltage sensor. We only need this information for debug reasons, so only query very infrequently.
        voltage = VoltageSensor()
        voltage.step_interval = 1000

        # Configure motors
        motors = Motors()
        motors.duration = 0.05
        motors.speed = 150

        # Pass the configuration to the robot.
        self.robot.sensors = [kinect, voltage]
        self.robot.actuators = [motors, KinectTiltMotor(), KinectLED()]

    def _prepare_robot(self):
        # Tilt Kinect to 20 degrees and disable LED to avoid reflections.
        self.robot.act([None, 20, KinectLEDAction.OFF])

    def _compute_new_state(self, action, sensor_data):
        depth_data = sensor_data[0]
        voltage = sensor_data[1]
        if voltage is not None:
            logging.info('system voltage is %fV' % voltage)

        # We reward as follows:
        # - if the robot is too close to an obstacle, every action is punished
        # - if the robot is not too close to an obstacle AND performs a forward action, reward
        # - if the robot is not too close to an obstacle AND performs a non-forward action, do neither punish nor reward
        mean_depth = np.mean(depth_data[depth_data < KINECT_INVALID_DEPTH])
        is_too_close = np.isnan(mean_depth) or mean_depth < 500.
        reward = 0
        if is_too_close:
            reward = -1
        elif action == MotorAction.FORWARD:
            reward = 1

        # Prepare remaining values.
        terminal = self._compute_error_rate(depth_data) > .8
        depth_data[depth_data == KINECT_INVALID_DEPTH] = 0  # replace errors with 0 -> assume very close approximity for errors
        frame = depth_data.astype('float32') / KINECT_INVALID_DEPTH
        lives = 1 if not terminal else 0

        return frame, reward, terminal, lives

    def _compute_error_rate(self, depth_data):
        n_depth_errors = np.sum(depth_data == KINECT_INVALID_DEPTH)
        return float(n_depth_errors) / float(np.size(depth_data))

    def reset(self):
        self.robot.act([None, None, KinectLEDAction.RED])
        while True:
            depth_data = self.robot.perceive()[0]
            error_rate = self._compute_error_rate(depth_data)
            mean_depth = np.mean(depth_data[depth_data < KINECT_INVALID_DEPTH])
            if error_rate < 0.2 and not np.isnan(mean_depth) and mean_depth > 800:
                break
            self._act(MotorAction.BACKWARD)
        self.robot.act([None, None, KinectLEDAction.OFF])


# class LightSeekingGameEnvironment(GameEnvironment):
#     def _compute_new_state(self, sensor_data):
#         assert len(sensor_data) >= 2
#         light = sensor_data[1]
#         if light > 80:
#             return 1
#         return 0
