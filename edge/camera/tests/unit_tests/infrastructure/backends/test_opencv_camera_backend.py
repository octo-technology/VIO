"""Unit tests for OpenCvCameraBackend.

cv2 is mocked via sys.modules injection before importing the backend so these
tests run without opencv installed (CI doesn't need the optional dependency).
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ── cv2 mock — must happen before any import of the backend ──────────────────

_mock_cap = MagicMock()
_mock_cap.read.return_value = (True, MagicMock())
_mock_cap.isOpened.return_value = True
# map CAP_PROP_* integer constants → realistic values
_mock_cap.get.side_effect = lambda prop: {3: 1920.0, 4: 1080.0, 5: 30.0}.get(prop, 0.0)


def _fake_imwrite(path: str, frame) -> bool:
    """Write a minimal valid JPEG so ImageRef.from_path can stat the file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
    return True


_mock_cv2 = MagicMock()
_mock_cv2.VideoCapture.return_value = _mock_cap
_mock_cv2.imwrite.side_effect = _fake_imwrite
_mock_cv2.CAP_PROP_FRAME_WIDTH = 3
_mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
_mock_cv2.CAP_PROP_FPS = 5

sys.modules.setdefault("cv2", _mock_cv2)

# ── imports (after mock injection) ───────────────────────────────────────────

from edge_camera.domain.ports.i_camera_backend import ICameraBackend  # noqa: E402
from edge_camera.infrastructure.backends.opencv_camera_backend import (  # noqa: E402
    OpenCvCameraBackend,
)


@pytest.fixture
def backend():
    return OpenCvCameraBackend(device_index=0)


def test_opencv_camera_implements_interface(backend):
    assert isinstance(backend, ICameraBackend)


async def test_capture_writes_jpeg_to_output_dir(backend, tmp_path):
    image_ref = await backend.capture(tmp_path, "cam_1")

    assert image_ref.camera_id == "cam_1"
    assert image_ref.size_bytes > 0
    assert image_ref.uri.startswith("file://")
    written_path = Path(image_ref.uri.replace("file://", ""))
    assert written_path.exists()
    assert written_path.suffix == ".jpg"


async def test_capture_uses_output_dir(backend, tmp_path):
    await backend.capture(tmp_path, "cam_1")

    jpegs = list(tmp_path.glob("*.jpg"))
    assert len(jpegs) == 1


async def test_capture_multiple_frames_produce_distinct_files(backend, tmp_path):
    ref1 = await backend.capture(tmp_path, "cam_1")
    await asyncio.sleep(0.01)
    ref2 = await backend.capture(tmp_path, "cam_1")

    assert ref1.uri != ref2.uri
    assert len(list(tmp_path.glob("*.jpg"))) == 2


def test_health_returns_ok(backend):
    h = backend.health()
    assert h["status"] == "ok"
    assert h["type"] == "opencv"
    assert h["device_index"] == 0


def test_metadata_returns_resolution(backend):
    m = backend.metadata()
    assert m["type"] == "opencv"
    assert "resolution" in m
    assert m["fps"] == 30.0


async def test_start_listening_calls_callback(backend, tmp_path):
    received = []

    async def on_frame(ref):
        received.append(ref)
        if len(received) >= 3:
            raise asyncio.CancelledError

    backend._frame_interval = 0.01
    try:
        await backend.start_listening(tmp_path, "cam_1", on_frame)
    except asyncio.CancelledError:
        pass

    assert len(received) >= 3
    for ref in received:
        assert ref.camera_id == "cam_1"
