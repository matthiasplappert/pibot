import logging
import select

import Pyro4
import Pyro4.core
import Pyro4.naming
import Pyro4.socketutil


class Robot(object):
    def __init__(self):
        self._sensors = []
        self._actuators = []
        self.n_steps = 0

    @property
    def actuators(self):
        return self._actuators

    @actuators.setter
    def actuators(self, val):
        self._actuators = val

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
        for actuator in self.actuators:
            if actuator.is_open:
                continue
            if not actuator.open():
                return False
        return True

    def close(self):
        for sensor in self.sensors:
            if not sensor.is_open:
                continue
            if not sensor.close():
                return False
        for actuator in self.actuators:
            if not actuator.is_open:
                continue
            if not actuator.close():
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

    def act(self, actions):
        if len(actions) != len(self.actuators):
            raise ValueError('must specify an action for each actuator')

        self.n_steps += 1
        for idx, actuator in enumerate(self.actuators):
            if not actuator.act(actions[idx]):
                logging.error('could not perform action on actuator %s' % actuator)


def run_robot(name, host, port):
    Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

    print('initializing robot "%s" ...' % name)
    robot = Robot()
    print('starting event loop ...')
    pyro_event_loop(name, robot, host=host, port=port)
    print('shutting down robot ...')


def get_remote_robot(name, host, port):
    # Use pickle for serialization (because we serialize numpy arrays).
    Pyro4.config.SERIALIZER = 'pickle'

    # Connect to robot and configure it.
    uri = 'PYRONAME:' + name
    if host is not None:
        uri += '@' + str(host)
        if port is not None:
            uri += ':' + str(port)
    return Pyro4.Proxy(uri)


def pyro_event_loop(name, obj, timeout=3.0, host=None, port=9090, callback=None):
    Pyro4.config.SERVERTYPE = 'thread'
    if host is None:
        host = Pyro4.socketutil.getIpAddress(None, workaround127=True)

    nameserverUri, nameserverDaemon, broadcastServer = Pyro4.naming.startNS(host=host, port=port)
    logging.info('name server uri: %s', nameserverUri)
    assert broadcastServer is not None
    daemon = Pyro4.core.Daemon(host=host)
    serverUri = daemon.register(obj)
    nameserverDaemon.nameserver.register(name, serverUri)

    # Event loop
    while True:
        # Create sets of the socket objects we will be waiting on
        nameserverSockets = set(nameserverDaemon.sockets)
        pyroSockets = set(daemon.sockets)
        rs = [broadcastServer]  # only the broadcast server is directly usable as a select() object
        rs.extend(nameserverSockets)
        rs.extend(pyroSockets)
        rs, _, _ = select.select(rs, [], [], timeout)
        eventsForNameserver = []
        eventsForDaemon = []
        for s in rs:
            if s is broadcastServer:
                broadcastServer.processRequest()
            elif s in nameserverSockets:
                eventsForNameserver.append(s)
            elif s in pyroSockets:
                eventsForDaemon.append(s)
        if eventsForNameserver:
            nameserverDaemon.events(eventsForNameserver)
        if eventsForDaemon:
            daemon.events(eventsForDaemon)

        if callback is not None and callable(callback):
            callback()

    nameserverDaemon.close()
    broadcastServer.close()
    daemon.close()
