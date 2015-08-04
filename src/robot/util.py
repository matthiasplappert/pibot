import select
import logging

import Pyro4.core
import Pyro4.naming
import Pyro4.socketutil
import freenect


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


class KinectDeviceManager(object):
    context = None
    device = None
    count = 0

    @staticmethod
    def open():
        KinectDeviceManager.count += 1
        if KinectDeviceManager.count > 1:
            return True
        context = freenect.init()
        if not context:
            return False
        device = freenect.open_device(context, 0)
        if not device:
            return False
        KinectDeviceManager.context = context
        KinectDeviceManager.device = device
        return True

    @staticmethod
    def close():
        KinectDeviceManager.count -= 1
        if KinectDeviceManager.count < 0:
            raise RuntimeError('unbalanced open and close call')
        elif KinectDeviceManager.count > 0:
            return True

        freenect.close_device(KinectDeviceManager.device)
        freenect.shutdown(KinectDeviceManager.context)
        KinectDeviceManager.device = None
        KinectDeviceManager.context = None
        return True
