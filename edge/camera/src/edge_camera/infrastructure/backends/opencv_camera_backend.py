import asyncio
from datetime import datetime
from pathlib import Path
from typing import Awaitable, Callable, Dict

try:
    import cv2

    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    cv2 = None  # type: ignore[assignment]

from edge_camera.domain.models.image_ref import ImageRef
from edge_camera.domain.ports.i_camera_backend import ICameraBackend


class OpenCvCameraBackend(ICameraBackend):
    """Camera backend using OpenCV VideoCapture (USB/CSI/V4L2 devices)."""

    def __init__(self, device_index: int = 0) -> None:
        if not _CV2_AVAILABLE:
            raise RuntimeError("opencv-python-headless is required: pip install 'edge_camera[opencv]'")
        self._device_index = device_index
        self._frame_interval: float = 1 / 30  # ~30 fps in push mode

    async def capture(self, output_dir: Path, camera_id: str) -> ImageRef:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._capture_sync, output_dir, camera_id)

    def _capture_sync(self, output_dir: Path, camera_id: str) -> ImageRef:
        cap = cv2.VideoCapture(self._device_index)
        try:
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError(f"Failed to read frame from device {self._device_index}")
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = output_dir / f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            cv2.imwrite(str(filename), frame)
            return ImageRef.from_path(filename, camera_id)
        finally:
            cap.release()

    async def start_listening(
        self,
        output_dir: Path,
        camera_id: str,
        on_frame: Callable[[ImageRef], Awaitable[None]],
    ) -> None:
        cap = cv2.VideoCapture(self._device_index)
        try:
            while True:
                ret, frame = cap.read()
                if ret:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    filename = output_dir / f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                    cv2.imwrite(str(filename), frame)
                    ref = ImageRef.from_path(filename, camera_id)
                    await on_frame(ref)
                await asyncio.sleep(self._frame_interval)
        finally:
            cap.release()

    def health(self) -> Dict:
        cap = cv2.VideoCapture(self._device_index)
        try:
            ok = cap.isOpened()
        finally:
            cap.release()
        return {"status": "ok" if ok else "error", "type": "opencv", "device_index": self._device_index}

    def metadata(self) -> Dict:
        cap = cv2.VideoCapture(self._device_index)
        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
        finally:
            cap.release()
        return {
            "type": "opencv",
            "device_index": self._device_index,
            "resolution": f"{width}x{height}",
            "fps": fps,
        }
