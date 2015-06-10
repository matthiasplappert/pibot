import pickle
import Pyro4


class Agent(object):
    def perceive(self, frame):
    	frame = pickle.loads(frame)
    	print frame.shape
        return "fwd"


def main():
	agent = Agent()
	daemon = Pyro4.Daemon()
	uri = daemon.register(agent)
	print("Ready. Object uri =", uri)
	daemon.requestLoop()


if __name__ == '__main__':
	main()
