import pickle
import Pyro4


class Agent(object):
    def perceive(self, input):
    	image = pickle.loads(input)
        print image.shape
        return "Hello"


def main():
	agent = Agent()
	daemon = Pyro4.Daemon()
	uri = daemon.register(agent)
	print("Ready. Object uri =", uri)
	daemon.requestLoop()


if __name__ == '__main__':
	main()
