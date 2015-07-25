import timeit

import freenect
import cv2


n_iterations = 1000
perform_resize = True
perform_crop = True

print('performing %d iterations ...' % n_iterations)
start = timeit.default_timer()
for _ in xrange(n_iterations):
	frame = freenect.sync_get_depth()[0]
	if perform_crop:
		min_dim = np.min(frame.shape)
		y_start, x_start = np.floor((frame.shape - min_dim) / 2)
		y_end, x_end = y_start + min_dim, x_start + min_dim
		frame = frame[y_start:y_end, x_start:x_end]
		assert frame.shape[0] == frame.shape[1]
	if perform_resize:
		frame = cv2.resize(frame, (78, 78))
		assert frame.shape == (78, 78)

duration = timeit.default_timer() - start
fps = int(float(n_iterations) / duration)
print('total time: %fs (%dfps)' % (duration, fps))
