import logging
import time

# Attempt to load gopigo, which is not available when simulating the robot.
try:
    import gopigo
    gopigo_available = True
except ImportError:
    gopigo_available = False


class Actuator(object):
    @property
    def actions(self):
        raise NotImplementedError()

    def act(self, action):
        if action not in self.actions:
            return False
        if action is None:
            # Do nothing, which is valid.
            return True
        return self._act(action)

    def _act(self, action):
        raise NotImplementedError()


class MotorAction(object):
    IDLE, FORWARD, BACKWARD, TURN_LEFT, TURN_RIGHT = range(5)


class Motors(Actuator):
    def __init__(self):
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
        return True
