import logging
import time

import Pyro4
# Attempt to load gopigo, which is not available when simulating the robot.
gopigo_available = True
try:
    import gopigo
except ImportError:
    gopigo_available = False

from util import pyro_event_loop


class Action(object):
    IDLE, FORWARD, BACKWARD, TURN_LEFT, TURN_RIGHT = range(5)


class Robot(object):
    def __init__(self):
        self._sensors = []
        self.n_steps = 0
        self._action_duration = .01

    @property
    def action_duration(self):
        return self._action_duration

    @action_duration.setter
    def action_duration(self, val):
        self._action_duration = val

    @property
    def sensors(self):
        return self._sensors

    @sensors.setter
    def sensors(self, val):
        self._sensors = val

    def open(self):
        for sensor in self.sensors:
            if sensor.is_open:
                continue
            if not sensor.open():
                return False
        return True

    def close(self):
        for sensor in self.sensors:
            if not sensor.is_open:
                continue
            if not sensor.close():
                return False
        return True

    def perceive(self):
        result = []
        for sensor in self.sensors:
            data = None
            if self.n_steps % sensor.step_interval == 0:
                data = sensor.perceive()
                if data is None:
                    logging.error('could not perceive with sensor %s' % sensor)
            result.append(data)
        return result

    @property
    def actions(self):
        return [Action.FORWARD, Action.BACKWARD, Action.IDLE, Action.TURN_LEFT, Action.TURN_RIGHT]

    def perform_action(self, action):
        self.n_steps += 1
        if not gopigo_available:
            logging.info('simulating action %d' % action)
            time.sleep(self.action_duration)
            return

        # Translate to action.
        if action == Action.TURN_LEFT:
            action_call = gopigo.left
        elif action == Action.TURN_RIGHT:
            action_call = gopigo.right
        elif action == Action.FORWARD:
            action_call = gopigo.fwd
        elif action == Action.BACKWARD:
            action_call = gopigo.bwd
        elif action == Action.IDLE:
            action_call = gopigo.stop
        else:
            action_call = None
        if action_call is None:
            raise ValueError('unknown action %d' % action)

        # Perform action for `duration` seconds and stop afterwards.
        logging.info('performing action %d' % action)
        action_call()
        time.sleep(self.action_duration)
        gopigo.stop()


def run_robot(name, host, port):
    Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

    print('initializing robot "%s" ...' % name)
    robot = Robot()
    print('starting event loop ...')
    pyro_event_loop(name, robot, host=host, port=port)
    print('shutting down robot ...')
