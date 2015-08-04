import logging
import time

import freenect
# Attempt to load gopigo, which is not available when simulating the robot.
try:
    import gopigo
    gopigo_available = True
except ImportError:
    gopigo_available = False


class Actuator(object):
    def __init__(self):
        self.is_open = False

    @property
    def actions(self):
        raise NotImplementedError()

    def open(self):
        if self.is_open or not self._open():
            logging.warning('cannot open sensor %s' % self)
            return False
        self.is_open = True
        return True

    def close(self):
        if not self.is_open or not self._close():
            logging.warning('cannot close sensor %s' % self)
            return False
        self.is_open = False
        return True

    def act(self, action):
        if not self.is_open:
            logging.warning('cannot act with closed actuator %s' % self)
            return False
        if action is None:
            # Do nothing, which is valid.
            return True
        if action not in self.actions:
            logging.warning('unknown action %s for actuator %s' % (action, self))
            return False
        return self._act(action)

    def _open(self):
        return True

    def _close(self):
        return True

    def _act(self, action):
        raise NotImplementedError()


class MotorAction(object):
    IDLE, FORWARD, BACKWARD, TURN_LEFT, TURN_RIGHT = range(5)


class Motors(Actuator):
    def __init__(self):
        super(Motors, self).__init__()
        self.duration = 0.05

    @property
    def actions(self):
        return [MotorAction.FORWARD, MotorAction.BACKWARD, MotorAction.IDLE, MotorAction.TURN_LEFT,
                MotorAction.TURN_RIGHT]

    def _act(self, action):
        if not gopigo_available:
            return False

        # Translate to action.
        if action == MotorAction.TURN_LEFT:
            action_call = gopigo.left
        elif action == MotorAction.TURN_RIGHT:
            action_call = gopigo.right
        elif action == MotorAction.FORWARD:
            action_call = gopigo.fwd
        elif action == MotorAction.BACKWARD:
            action_call = gopigo.bwd
        elif action == MotorAction.IDLE:
            action_call = gopigo.stop
        else:
            action_call = None
        assert action_call is not None

        # Perform action for `duration` seconds and stop afterwards.
        logging.info('performing motor action %d' % action)
        action_call()
        time.sleep(self.duration)
        gopigo.stop()
        return True


class SimulatedMotors(Motors):
    def _act(self, action):
        logging.info('simulating motor action %d' % action)
        time.sleep(self.duration)
        return True


class KinectTiltMotor(Actuator):
    def _open(self):
        return freenect.sync_get_tilt_state() is not None

    @property
    def actions(self):
        return range(-20, 21)  # [-20, 20]

    def _act(self, action):
        return freenect.sync_set_tilt_degs(action) == 0


class KinectLEDAction(object):
    OFF = freenect.LED_OFF
    GREEN = freenect.LED_GREEN
    RED = freenect.LED_RED
    YELLOW = freenect.LED_YELLOW
    BLINK_GREEN = freenect.LED_BLINK_GREEN
    BLINK_RED_YELLOW = freenect.LED_BLINK_RED_YELLOW


class KinectLED(Actuator):
    def _open(self):
        return freenect.sync_get_tilt_state() is not None

    @property
    def actions(self):
        return [KinectLEDAction.OFF, KinectLEDAction.GREEN, KinectLEDAction.RED, KinectLEDAction.YELLOW,
                KinectLEDAction.BLINK_GREEN, KinectLEDAction.BLINK_RED_YELLOW]

    def _act(self, action):
        return freenect.sync_set_led(action) == 0
