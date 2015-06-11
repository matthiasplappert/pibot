import os

import pickle
import Pyro4
import scipy.misc

import actions


class Agent(object):
    def __init__(self):
        self.path = '/Users/matze/Desktop/current.png'
        self._config = {
            'image_gray': True,
            'image_crop': True,
            'image_resize': (84, 84)
        }

    def client_config(self):
        return self._config

    def perceive(self, frame):
        frame = pickle.loads(frame)
        if os.path.exists(self.path):
            os.remove(self.path)
        scipy.misc.toimage(frame, cmin=0.0, cmax=1.0).save(self.path)
        return actions.ABORT


def main():
    agent = Agent()
    daemon = Pyro4.Daemon()
    uri = daemon.register(agent)
    print("Ready. Object uri =", uri)
    daemon.requestLoop()


if __name__ == '__main__':
    main()
