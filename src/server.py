import pickle
import select
import threading

import cv2
import Pyro4
import scipy.misc
import numpy as np
import Pyro4.core
import Pyro4.naming
import Pyro4.socketutil

import actions


class Agent(object):
    def __init__(self):
        self._last_frame = None
        self._last_frame_lock = threading.Lock()
        self.path = '/Users/matze/Desktop/current.png'
        self._config = {
            'image_gray': True,
            'image_crop': True,
            'image_resize': (84, 84),
        }

    def config(self):
        return self._config

    @property
    def last_frame(self):
        self._last_frame_lock.acquire()
        value = self._last_frame
        self._last_frame_lock.release()
        return value

    @last_frame.setter
    def last_frame(self, value):
        self._last_frame_lock.acquire()
        self._last_frame = value
        self._last_frame_lock.release()

    def perceive(self, frame):
        frame = pickle.loads(frame)
        frame = frame.astype(float) / 255.0  # normalize to [0,1]
        self.last_frame = frame

        # Calculate average brightness
        # TODO: add some sort of flexible interface that calculates a score from the frame
        avg = np.average(frame)
        print avg

        return actions.STOP


def main():
    agent = Agent()

    cv2.namedWindow('preview')
    event_loop(agent)
    cv2.destroyWindow()

def event_loop(server):
    Pyro4.config.SERVERTYPE = 'thread'
    my_ip = Pyro4.socketutil.getIpAddress(None, workaround127=True)

    print('initializing server ...')
    nameserverUri, nameserverDaemon, broadcastServer = Pyro4.naming.startNS(host=my_ip)
    assert broadcastServer is not None

    # Create a Pyro daemon
    daemon = Pyro4.core.Daemon(host=my_ip)
    print('daemon location string=%s' % daemon.locationStr)

    # Register a server object with the daemon
    serverUri = daemon.register(server)
    print("server uri=%s" % serverUri)

    # Register it with the embedded nameserver directly
    nameserverDaemon.nameserver.register('agent', serverUri)
    print('done!\n')

    # Event loop
    while True:
        # Create sets of the socket objects we will be waiting on
        nameserverSockets = set(nameserverDaemon.sockets)
        pyroSockets = set(daemon.sockets)
        rs = [broadcastServer]  # only the broadcast server is directly usable as a select() object
        rs.extend(nameserverSockets)
        rs.extend(pyroSockets)
        rs, _, _ = select.select(rs, [], [], 0.1)
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

        # Display last frame
        frame = server.last_frame
        if frame is not None:
            cv2.imshow('preview', frame)
            cv2.waitKey(1)

    nameserverDaemon.close()
    broadcastServer.close()
    daemon.close()
    print('server shutting down')


if __name__ == '__main__':
    main()
