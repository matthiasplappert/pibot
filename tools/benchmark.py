import freenect
import timeit

n_iterations = 1000
start = timeit.default_timer()
for _ in xrange(n_iterations)
	freenect.sync_get_depth()
duration = timeit.default_timer() - start
fps = int(float(n_iterations) / duration)
print('performed %d iterations: total time: %fs (%dfps)' % (n_iterations, duration, fps))
