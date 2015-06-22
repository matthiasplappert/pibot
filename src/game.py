import Pyro4
import cv2
import numpy as np


class GameEnvironment(object):
    def __init__(self, name, host=None, port=None, grayscale=True, crop=True, resize=(84, 84)):
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

    def step(self, action):
        # Reward should be either -1, 0, or 1
        frame, reward, terminal, lives, _ = self.debug_step(action)
        return frame, reward, terminal, lives

    def debug_step(self, action):
        self.agent.perform_action(action)
        frame = self.agent.perceive(grayscale=self.grayscale, crop=self.crop, resize=self.resize)

        if action == 3:
            processed_frame = np.ones(frame.shape)
            reward = 1
        else:
            processed_frame = np.zeros(frame.shape)
            reward = 0
        return frame.astype(float) / 255.0, reward, False, 1, processed_frame

        # Calculate current score:
        # Step 1: Apply Gaussian blur to decrease noise
        # Step 2: Apply binary threshold to binary seperate bright from dark spots
        # Step 3: Calculate score as average over entire image, which will be maximal if the entire image is bright
        processed_frame = cv2.GaussianBlur(frame, (21, 21), 0)
        _, processed_frame = cv2.threshold(processed_frame, 200, 255, cv2.THRESH_BINARY)
        processed_frame = processed_frame.astype(float) / 255.0

        # Calculate reward and related values
        score = np.average(processed_frame)  # score in [0,1]
        reward = 0
        if score > 0.05:
            # At least 5% of the image are bright, reward the agent
            reward = 1
        terminal = False
        lives = 1
        return frame.astype(float) / 255.0, reward, terminal, lives, processed_frame

    def get_actions(self):
        return self.agent.get_actions()
