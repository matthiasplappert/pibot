import argparse
import pickle
import timeit

import cv2
import Pyro4

import actions


def main(args):
    if args.debug_frames:
        cv2.namedWindow('debug-frames')

    prev_score = 0
    agent = Pyro4.Proxy('PYRONAME:' + args.agent)
    while True:
        start = timeit.default_timer()
        frame = pickle.loads(agent.perceive(grayscale=True, crop=True, resize=(84, 84)))
        if frame is None:
            print('skipping frame')
            continue

        if args.debug_frames:
            cv2.imshow('debug-frames', frame)
            cv2.waitKey(1)

        #frame = frame.astype(float) / 255.0  # normalize to [0,1]

        # Calculate histogram over 16 bins. We then select the top bin. Our agent likes light, so the more
        # pixels we have in the top bin, the bigger a bright spot in the image is. Our agent is very happy if the
        # entire image is just a bright spot.
        histogram = cv2.calcHist([frame], [0], None, [16], [0, 256])[:, 0]
        print histogram
        score = histogram[-1]
        delta = score - prev_score
        prev_score = score

        print('score=%d (delta=%d)' % (score, delta))

        agent.perform_action(actions.STOP)
        duration = timeit.default_timer() - start
        print('perceive-action cycle took %fs\n' % duration)

    if args.debug_frames:
        cv2.destroyWindow()


def get_parser():
    parser = argparse.ArgumentParser(description='Server for nn-robot.')
    parser.add_argument('--debug-frames', action='store_true', help='display each frame')
    parser.add_argument('agent', help='name of the agent')
    return parser


if __name__ == '__main__':
    main(get_parser().parse_args())
