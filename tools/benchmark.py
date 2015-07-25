import freenect
import timeit

n_iterations = 1000
print('performing %d iterations ...' % n_iterations)
start = timeit.default_timer()
for _ in xrange(n_iterations):
	freenect.sync_get_depth()
duration = timeit.default_timer() - start
fps = int(float(n_iterations) / duration)
print('total time: %fs (%dfps)' % (duration, fps))
