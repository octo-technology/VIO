import asyncio
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Awaitable, Callable, Dict, Optional

try:
    from pypylon import pylon

    _PYPYLON_AVAILABLE = True
except ImportError:
    _PYPYLON_AVAILABLE = False
    pylon = None  # type: ignore[assignment]

from edge_camera.domain.models.image_ref import ImageRef
from edge_camera.domain.ports.i_camera_backend import ICameraBackend

_GRAB_TIMEOUT_MS = 5_000


class BaslerCameraBackend(ICameraBackend):
    """Camera backend using pypylon for Basler GigE/USB3 Vision cameras."""

    def __init__(self, serial_number: Optional[str] = None) -> None:
        if not _PYPYLON_AVAILABLE:
            raise RuntimeError("pypylon is required: pip install 'edge_camera[basler]'")
        self._serial_number = serial_number
        self._frame_interval: float = 1 / 30  # ~30 fps in push mode

    def _open_camera(self):
        factory = pylon.TlFactory.GetInstance()
        if self._serial_number:
            info = pylon.DeviceInfo()
            info.SetSerialNumber(self._serial_number)
            device = factory.CreateDevice(info)
        else:
            device = factory.CreateFirstDevice()
        return pylon.InstantCamera(device)

    def _grab_jpeg(self, camera) -> bytes:
        """Grab one frame and return it encoded as JPEG bytes."""
        from PIL import Image as PilImage

        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        try:
            grab_result = camera.RetrieveResult(_GRAB_TIMEOUT_MS, pylon.TimeoutHandling_ThrowException)
            with grab_result:
                if not grab_result.GrabSucceeded():
                    raise RuntimeError(f"Grab failed: {grab_result.ErrorDescription}")
                array = grab_result.GetArray()
                img = PilImage.fromarray(array)
                buf = BytesIO()
                img.save(buf, format="JPEG")
                return buf.getvalue()
        finally:
            camera.StopGrabbing()

    async def capture(self, output_dir: Path, camera_id: str) -> ImageRef:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._capture_sync, output_dir, camera_id)

    def _capture_sync(self, output_dir: Path, camera_id: str) -> ImageRef:
        camera = self._open_camera()
        try:
            camera.Open()
            jpeg_bytes = self._grab_jpeg(camera)
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = output_dir / f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            filename.write_bytes(jpeg_bytes)
            return ImageRef.from_path(filename, camera_id)
        finally:
            camera.Close()

    async def start_listening(
        self,
        output_dir: Path,
        camera_id: str,
        on_frame: Callable[[ImageRef], Awaitable[None]],
    ) -> None:
        loop = asyncio.get_event_loop()
        camera = self._open_camera()
        try:
            camera.Open()
            while True:
                jpeg_bytes = await loop.run_in_executor(None, self._grab_jpeg, camera)
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = output_dir / f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                filename.write_bytes(jpeg_bytes)
                ref = ImageRef.from_path(filename, camera_id)
                await on_frame(ref)
                await asyncio.sleep(self._frame_interval)
        finally:
            camera.Close()

    def health(self) -> Dict:
        try:
            camera = self._open_camera()
            camera.Open()
            camera.Close()
            return {"status": "ok", "type": "basler", "serial_number": self._serial_number}
        except Exception as exc:
            return {"status": "error", "type": "basler", "serial_number": self._serial_number, "error": str(exc)}

    def metadata(self) -> Dict:
        camera = self._open_camera()
        try:
            camera.Open()
            info = camera.GetDeviceInfo()
            return {
                "type": "basler",
                "serial_number": info.GetSerialNumber(),
                "model": info.GetModelName(),
                "vendor": info.GetVendorName(),
            }
        finally:
            camera.Close()
