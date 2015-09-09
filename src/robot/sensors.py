import logging

import numpy as np
import freenect
import cv2
try:
    import gopigo
    gopigo_available = True
except ImportError:
    gopigo_available = False


KINECT_INVALID_DEPTH = 2047


class Sensor(object):
    def __init__(self):
        self.step_interval = 1
        self.is_open = False

    def perceive(self):
        if not self.is_open:
            logging.warning('cannot perceive with closed sensor %s' % self)
            return None
        data = self._perceive()
        if data is None:
            return None
        return self._process_data(data)

    def open(self):
        if self.is_open or not self._open():
            logging.warning('cannot open sensor %s' % self)
            return False
        self.is_open = True
        return True

    def close(self):
        if not self.is_open or not self._close():
            logging.warning('cannot close sensor %s' % self)
            return False
        self.is_open = False
        return True

    def _perceive(self):
        raise NotImplementedError()

    def _process_data(self, data):
        assert data is not None
        return data

    def _open(self):
        return True

    def _close(self):
        return True


class Camera(Sensor):
    def __init__(self):
        super(Camera, self).__init__()
        self.convert_color = cv2.COLOR_BGR2RGB
        self.crop = True
        self.resize = (100, 100)

    def _process_data(self, data):
        assert data is not None

        if self.convert_color is not None:
            data = cv2.cvtColor(data, self.convert_color)

        # Ensure that we have exactly 3 dimensions: (height, width, channel). This makes cropping easier.
        assert data.ndim in (2, 3)
        if data.ndim == 2:
            data = data.reshape(data.shape + (1,))
        assert data.ndim == 3
        if self.crop:
            image_shape = data.shape[:2]  # = (height, width)
            min_dim = np.min(image_shape)
            y_start, x_start = np.floor((image_shape - min_dim) / 2)
            y_end, x_end = y_start + min_dim, x_start + min_dim
            data = data[y_start:y_end, x_start:x_end, :]
            assert data.shape[0] == data.shape[1]
        if data.shape[2] == 1:
            # Convert back to two dimensions. We do this because cv2.resize() will return a 2-dim array if an image has
            # only one channel. As a result, the return type would be different depending on the set options.
            data = data.reshape(data.shape[:2])
        if self.resize is not None:
            data = cv2.resize(data, self.resize)
        return data

    def _perceive(self):
        raise NotImplementedError()


class KinectDepthCamera(Camera):
    def __init__(self):
        super(KinectDepthCamera, self).__init__()
        self.convert_color = None

    def _open(self):
        return freenect.sync_get_tilt_state() is not None

    def _perceive(self):
        result = freenect.sync_get_depth()
        if result is None:
            return None
        return result[0]  # result = (data, timestamp)


class KinectVideoCamera(Camera):
    def _open(self):
        return freenect.sync_get_tilt_state() is not None

    def _perceive(self):
        result = freenect.sync_get_video()
        if result is None:
            return None
        return result[0]  # result = (data, timestamp)


class KinectTiltSensor(Sensor):
    def _open(self):
        return freenect.sync_get_tilt_state() is not None

    def _perceive(self):
        state = freenect.sync_get_tilt_state()
        acceleration = freenect.get_mks_accel(state)
        return (state.tilt_angle, state.tilt_status) + acceleration


class OpenCVCamera(Camera):
    def __init__(self):
        super(OpenCVCamera, self).__init__()
        self.video_capture = None
        self.n_grabs = 1
        self.camera_index = 0

    def _perceive(self):
        if self.video_capture is None or not self.video_capture.isOpened():
            return None

        # Read potentially multiple times to avoid reading stalled data from the internal buffer.
        for _ in xrange(self.n_grabs):
            self.video_capture.grab()
        success, frame = self.video_capture.retrieve()
        if not success:
            return None
        return frame

    def _open(self):
        assert self.video_capture is None
        try:
            vc = cv2.VideoCapture()
            vc.open(self.camera_index)
        except:
            return False
        if not vc.isOpened():
            return False
        vc.set(cv2.cv.CV_CAP_PROP_CONVERT_RGB, True)
        self.video_capture = vc
        return True

    def _close(self):
        assert self.video_capture is not None
        self.video_capture.release()
        self.video_capture = None
        return True


class AnalogSensor(Sensor):
    def __init__(self):
        super(AnalogSensor, self).__init__()
        self.pin = 1

    def _open(self):
        if not gopigo_available:
            return False
        gopigo.pinMode(self.pin, 'INPUT')
        return True

    def _perceive(self):
        if not gopigo_available:
            return None
        value = gopigo.analogRead(self.pin)
        if value < 0:
            return None
        return value


class VoltageSensor(Sensor):
    def _perceive(self):
        if not gopigo_available:
            return None
        return gopigo.volt()
