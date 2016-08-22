import logging
import time

try:
    import freenect
    import cv2
except ImportError:
    pass
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
        self.speed = 150

    def _open(self):
        if not gopigo_available:
            return False
        gopigo.set_speed(self.speed)
        return True

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
        return True


class SimulatedMotors(Motors):
    def _act(self, action):
        logging.info('simulating motor action %d' % action)
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
    OFF = 0
    GREEN = 1
    RED = 2
    YELLOW = 3
    BLINK_GREEN = 4
    BLINK_RED_YELLOW = 5


class KinectLED(Actuator):
    def _open(self):
        return freenect.sync_get_tilt_state() is not None

    @property
    def actions(self):
        return [KinectLEDAction.OFF, KinectLEDAction.GREEN, KinectLEDAction.RED, KinectLEDAction.YELLOW,
                KinectLEDAction.BLINK_GREEN, KinectLEDAction.BLINK_RED_YELLOW]

    def _act(self, action):
        kinect_action = None
        if action == KinectLEDAction.OFF:
            kinect_action = freenect.LED_OFF
        elif action == KinectLEDAction.GREEN:
            kinect_action = freenect.LED_GREEN
        elif action == KinectLEDAction.RED:
            kinect_action = freenect.LED_RED
        elif action == KinectLEDAction.YELLOW:
            kinect_action = freenect.LED_YELLOW
        elif action == KinectLEDAction.BLINK_GREEN:
            kinect_action = freenect.LED_BLINK_GREEN
        elif action == KinectLEDAction.BLINK_RED_YELLOW:
            kinect_action = freenect.LED_BLINK_RED_YELLOW
        else:
            raise RuntimeError('Unknown action {}.'.format(action))
        assert kinect_action is not None
        return freenect.sync_set_led(action) == 0
