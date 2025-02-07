import logging
from typing import Iterator

import cv2
import numpy as np
from tenacity import retry, stop_after_attempt, wait_fixed

from edge_orchestrator.domain.models.binary import Image
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class WebcamCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        self._cap = None
        self._open_webcam(iter([0, 1, 2, 3]))

    @retry(stop=stop_after_attempt(4), wait=wait_fixed(2))
    def _open_webcam(self, device_stream: Iterator):
        self._cap = cv2.VideoCapture(next(device_stream))

        if not self._cap.isOpened():
            raise cv2.error("Could not open webcam")

        if self._camera_config.camera_resolution:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._camera_config.camera_resolution.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._camera_config.camera_resolution.height)

    def _release_webcam(self):
        try:
            self._cap.release()
        except cv2.error:
            self._logger.warning("Could not release properly the webcam")

    def capture(self, attempt=0) -> Image:
        exit_code, frame = self._cap.read()
        if not exit_code and attempt < 5:
            self._logger.error("Failed to capture image")
            self._open_webcam(iter([0, 1, 2, 3]))
            self.capture(attempt+1)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        exit_code, img_encode = cv2.imencode(".jpg", frame_rgb)
        img_as_array = np.array(img_encode)
        return Image(image_bytes=img_as_array.tobytes())

    def get_camera_config(self) -> CameraConfig:
        return self._camera_config
