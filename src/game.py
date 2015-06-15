import pickle

import Pyro4
import cv2


class GameEnvironment(object):
    def __init__(self, name, host=None, port=None, grayscale=True, crop=True, resize=(84, 84)):
        uri = 'PYRONAME:' + name
        if host is not None:
            uri += '@' + str(host)
            if port is not None:
                uri += ':' + str(port)
        self.agent = Pyro4.Proxy(uri)
        self.grayscale = grayscale
        self.crop = crop
        self.resize = resize
        self.prev_score = 0

    def step(self, action):
        self.agent.perform_action(action)
        frame = pickle.loads(self.agent.perceive(grayscale=self.grayscale, crop=self.crop, resize=self.resize))

        # Calculate histogram over 16 bins. We then select the top bin. Our agent likes light, so the more
        # pixels we have in the top bin, the bigger a bright spot in the image is. Our agent is very happy if the
        # entire image is just a bright spot.
        n_bins = 16
        histogram = cv2.calcHist([frame], [0], None, [n_bins], [0, 255])[:, 0]
        curr_score = histogram[-1]
        if curr_score == 0:
            curr_score = 1
        delta = curr_score - self.prev_score
        print abs(delta) / curr_score
        reward = 0
        if abs(delta) / curr_score > 0.1:
            if delta > 0:
                reward = 1
            else:
                reward = -1
        self.prev_score = curr_score

        # TODO: maybe use those?
        terminal = False
        lives = 1
        return frame.astype(float) / 255.0, reward, terminal, lives