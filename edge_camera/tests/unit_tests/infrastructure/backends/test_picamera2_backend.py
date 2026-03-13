"""Unit tests for Picamera2Backend.

picamera2 is mocked via sys.modules injection before importing the backend so
these tests run without the library installed (CI doesn't need the RPi dep).
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ── picamera2 mock — must happen before any import of the backend ─────────────


def _fake_capture_file(path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)


_mock_cam_instance = MagicMock()
_mock_cam_instance.capture_file.side_effect = _fake_capture_file
_mock_cam_instance.camera_properties = {
    "Model": "imx477",
    "PixelArraySize": [4056, 3040],
}

_mock_picamera2_module = MagicMock()
_mock_picamera2_module.Picamera2.return_value = _mock_cam_instance

sys.modules.setdefault("picamera2", _mock_picamera2_module)

# ── imports (after mock injection) ────────────────────────────────────────────

from edge_camera.domain.ports.i_camera_backend import ICameraBackend  # noqa: E402
from edge_camera.infrastructure.backends.picamera2_backend import (  # noqa: E402
    Picamera2Backend,
)


@pytest.fixture(autouse=True)
def reset_mock():
    """Reset call counts between tests."""
    _mock_cam_instance.reset_mock()
    _mock_cam_instance.capture_file.side_effect = _fake_capture_file
    _mock_cam_instance.camera_properties = {
        "Model": "imx477",
        "PixelArraySize": [4056, 3040],
    }


@pytest.fixture
def backend():
    return Picamera2Backend(camera_num=0)


def test_picamera2_backend_implements_interface(backend):
    assert isinstance(backend, ICameraBackend)


async def test_capture_writes_jpeg_to_output_dir(backend, tmp_path):
    image_ref = await backend.capture(tmp_path, "cam_rpi")

    assert image_ref.camera_id == "cam_rpi"
    assert image_ref.size_bytes > 0
    assert image_ref.uri.startswith("file://")
    written_path = Path(image_ref.uri.replace("file://", ""))
    assert written_path.exists()
    assert written_path.suffix == ".jpg"


async def test_capture_opens_and_closes_camera(backend, tmp_path):
    await backend.capture(tmp_path, "cam_rpi")

    _mock_cam_instance.start.assert_called_once()
    _mock_cam_instance.stop.assert_called_once()
    _mock_cam_instance.close.assert_called_once()


async def test_capture_multiple_frames_produce_distinct_files(backend, tmp_path):
    ref1 = await backend.capture(tmp_path, "cam_rpi")
    await asyncio.sleep(0.01)
    ref2 = await backend.capture(tmp_path, "cam_rpi")

    assert ref1.uri != ref2.uri
    assert len(list(tmp_path.glob("*.jpg"))) == 2


def test_health_returns_ok(backend):
    h = backend.health()

    assert h["status"] == "ok"
    assert h["type"] == "picamera2"
    assert h["camera_num"] == 0


def test_health_returns_error_when_camera_raises(backend):
    _mock_picamera2_module.Picamera2.side_effect = RuntimeError("no camera found")
    try:
        h = backend.health()
        assert h["status"] == "error"
        assert "no camera found" in h["error"]
    finally:
        _mock_picamera2_module.Picamera2.side_effect = None
        _mock_picamera2_module.Picamera2.return_value = _mock_cam_instance


def test_metadata_returns_model_and_resolution(backend):
    m = backend.metadata()

    assert m["type"] == "picamera2"
    assert m["model"] == "imx477"
    assert m["resolution"] == "4056x3040"
    assert m["camera_num"] == 0


async def test_start_listening_calls_callback(backend, tmp_path):
    received = []

    async def on_frame(ref):
        received.append(ref)
        if len(received) >= 3:
            raise asyncio.CancelledError

    backend._frame_interval = 0.01
    try:
        await backend.start_listening(tmp_path, "cam_rpi", on_frame)
    except asyncio.CancelledError:
        pass

    assert len(received) >= 3
    for ref in received:
        assert ref.camera_id == "cam_rpi"


async def test_start_listening_closes_camera_on_cancel(backend, tmp_path):
    async def on_frame(ref):
        raise asyncio.CancelledError

    backend._frame_interval = 0.01
    try:
        await backend.start_listening(tmp_path, "cam_rpi", on_frame)
    except asyncio.CancelledError:
        pass

    _mock_cam_instance.stop.assert_called_once()
    _mock_cam_instance.close.assert_called_once()
