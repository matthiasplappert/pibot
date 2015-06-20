from collections import deque

import Pyro4
import cv2
import numpy as np


class GameEnvironment(object):
    def __init__(self, name, host=None, port=None, grayscale=True, crop=True, resize=(84, 84), sliding_window=5):
        # Use pickle for serialization
        Pyro4.config.SERIALIZER = 'pickle'

        uri = 'PYRONAME:' + name
        if host is not None:
            uri += '@' + str(host)
            if port is not None:
                uri += ':' + str(port)
        self.agent = Pyro4.Proxy(uri)
        self.grayscale = grayscale
        self.crop = crop
        self.resize = resize
        self.scores = deque(maxlen=sliding_window)

    def step(self, action):
        # Reward should be either -1, 0, or 1
        frame, reward, terminal, lives, _ = self.debug_step(action)
        return frame, reward, terminal, lives

    def debug_step(self, action):
        self.agent.perform_action(action)
        frame = self.agent.perceive(grayscale=self.grayscale, crop=self.crop, resize=self.resize)

        # Calculate current score:
        # Step 1: Apply Gaussian blur to decrease noise
        # Step 2: Apply binary threshold to binary seperate bright from dark spots
        # Step 3: Calculate score as average over entire image, which will be maximal if the entire image is bright
        processed_frame = cv2.GaussianBlur(frame, (21, 21), 0)
        _, processed_frame = cv2.threshold(processed_frame, 200, 255, cv2.THRESH_BINARY)
        processed_frame = processed_frame.astype(float) / 255.0
        score = np.average(processed_frame)  # score in [0,1]
        if score == 0.0:
            # Use a very small score to avoid division by zero
            score = np.finfo(float).eps

        # Calculate reward: We use a sliding window to smooth the score function and remove jitter. If the sliding
        # window is not full yet, assume a reward of 0 and wait until it fills
        reward = 0
        if len(self.scores) == self.scores.maxlen:
            # Only calculate reward if we have enough data in our sliding window
            prev_score = np.average(self.scores)
            delta = score - prev_score
            if abs(delta) / score > 0.1:
                if delta > 0:
                    reward = 1
                else:
                    reward = -1
        self.scores.append(score)

        # TODO: maybe use those later?
        terminal = False
        lives = 1
        return frame.astype(float) / 255.0, reward, terminal, lives, processed_frame

    def get_actions(self):
        return self.agent.get_actions()
