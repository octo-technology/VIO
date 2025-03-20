import logging
from threading import Thread
from typing import Dict, Optional, Tuple, Union

import cv2
import numpy as np

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.image import Image
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.infrastructure.adapters.camera.usb_device import (
    list_connected_usb_device,
)


class UsbCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        try:
            usb_devices = list_connected_usb_device()
            device_node = self._get_camera_device_node(
                usb_devices,
                camera_config.camera_vendor,
                camera_config.camera_serial_number,
                camera_config.same_camera_index,
            )
            self._open_webcam(device_node)
            self._start()
        except Exception:
            self._logger.exception(f"Error while opening USB camera: {self._camera_config.camera_id}")

    @staticmethod
    def _get_camera_device_node(
        usb_devices: Dict[Tuple, str], camera_vendor: str, camera_serial_number: str, same_camera_index: int
    ) -> Optional[str]:
        corresponding_devices = []
        for cam_vendor, cam_serial_number, id_path in usb_devices.keys():
            if camera_vendor == cam_vendor and camera_serial_number == cam_serial_number:
                corresponding_devices.append(usb_devices[(cam_vendor, cam_serial_number, id_path)]["device_path"])
        if len(corresponding_devices) == 0:
            logging.warning(
                f"Camera with vendor: {camera_vendor} and serial number: {camera_serial_number} not found in connected USB devices:\n{usb_devices}"
            )
            return None
        else:
            logging.warning(f"Found several devices with the same vendor and serial number: {corresponding_devices}")
            logging.warning(f"Returning the device at index: {same_camera_index}")
            return corresponding_devices[same_camera_index]

    def _open_webcam(self, src_or_index: Union[str, int]):
        self._stream = cv2.VideoCapture(src_or_index)
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
