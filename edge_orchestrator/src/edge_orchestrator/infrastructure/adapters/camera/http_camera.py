import logging
from pathlib import Path

import httpx

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item import Image
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class HttpCamera(ICamera):
    """Pull-mode camera adapter: delegates capture to the edge_camera HTTP service.

    The service URL is taken from camera_config.service_url (default: http://localhost:8001).
    The service returns an ImageRef JSON with a uri field.  File URIs (file://)
    are resolved by reading the file directly (same-host deployment).
    HTTP URIs are fetched from the network.
    """

    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        base_url = camera_config.service_url.rstrip("/")
        self._capture_url = f"{base_url}/capture"

    def capture(self) -> Image:
        response = httpx.post(
            self._capture_url,
            params={"camera_id": self._camera_config.camera_id},
            timeout=10.0,
        )
        response.raise_for_status()
        image_ref = response.json()
        image_bytes = self._resolve_bytes(image_ref["uri"])
        return Image(image_bytes=image_bytes)

    def _resolve_bytes(self, uri: str) -> bytes:
        if uri.startswith("file://"):
            return Path(uri[len("file://") :]).read_bytes()
        return httpx.get(uri, timeout=10.0).content
