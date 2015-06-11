import os
import pickle

import Pyro4
import scipy.misc
import numpy as np

import actions


class Agent(object):
    def __init__(self):

        self.path = '/Users/matze/Desktop/current.png'
        self._config = {
            'image_gray': True,
            'image_crop': True,
            'image_resize': (84, 84),
        }

    def config(self):
        return self._config

    def perceive(self, frame):
        frame = pickle.loads(frame)
        frame = frame.astype(float) / 255.0  # normalize to [0,1]

        # Calculate average brightness
        # TODO: add some sort of flexible interface that calculates a score from the frame
        avg = np.average(frame)
        print avg

        # Save image
        if os.path.exists(self.path):
            os.remove(self.path)
        scipy.misc.toimage(frame, cmin=0.0, cmax=1.0).save(self.path)
        return actions.STOP


def main():
    agent = Agent()
    daemon = Pyro4.Daemon('192.168.1.57')
    uri = daemon.register(agent)
    print("Ready. Object uri =", uri)
    daemon.requestLoop()


if __name__ == '__main__':
    main()
