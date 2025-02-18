import logging
from threading import Thread

import cv2
import numpy as np

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.image import Image
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class WebcamCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        self._open_webcam(self._camera_config.source_directory.as_posix())
        self._start()

    def _open_webcam(self, src: str):
        self._stream = cv2.VideoCapture(src)
        (self._grabbed, self._frame) = self._stream.read()
        self._name = __name__
        self._stopped = False
        if self._camera_config.camera_resolution:
            self._stream.set(cv2.CAP_PROP_FRAME_WIDTH, self._camera_config.camera_resolution.width)
            self._stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self._camera_config.camera_resolution.height)

    def _start(self):
        t = Thread(target=self._update, name=self._name, args=())
        t.daemon = True
        t.start()

    def _update(self):
        while True:
            if self._stopped:
                return
            (self._grabbed, self._frame) = self._stream.read()

    def release(self):
        self._stopped = True
        self._stream.release()

    def capture(self) -> Image:
        _, img_encode = cv2.imencode(".jpg", self._frame)
        img_as_array = np.array(img_encode)
        return Image(image_bytes=img_as_array.tobytes())
