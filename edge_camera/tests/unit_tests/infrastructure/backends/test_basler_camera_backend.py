"""Unit tests for BaslerCameraBackend.

pypylon is mocked via sys.modules injection before importing the backend so
these tests run without the library or hardware installed.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

# ── pypylon mock — must happen before any import of the backend ───────────────

# GrabResult mock — GetArray returns a real numpy frame so PIL.fromarray works
_mock_grab_result = MagicMock()
_mock_grab_result.GrabSucceeded.return_value = True
_mock_grab_result.GetArray.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
_mock_grab_result.__enter__ = lambda s: s
_mock_grab_result.__exit__ = MagicMock(return_value=False)

# DeviceInfo mock
_mock_device_info = MagicMock()
_mock_device_info.GetSerialNumber.return_value = "12345678"
_mock_device_info.GetModelName.return_value = "acA1920-40gc"
_mock_device_info.GetVendorName.return_value = "Basler"

# Camera mock
_mock_camera = MagicMock()
_mock_camera.RetrieveResult.return_value = _mock_grab_result
_mock_camera.GetDeviceInfo.return_value = _mock_device_info

# pylon module mock
_mock_pylon = MagicMock()
_mock_pylon.InstantCamera.return_value = _mock_camera
_mock_pylon.GrabStrategy_LatestImageOnly = 1
_mock_pylon.TimeoutHandling_ThrowException = 0

_mock_pypylon = MagicMock()
_mock_pypylon.pylon = _mock_pylon

sys.modules.setdefault("pypylon", _mock_pypylon)
sys.modules.setdefault("pypylon.pylon", _mock_pylon)

# ── imports (after mock injection) ────────────────────────────────────────────

from edge_camera.domain.ports.i_camera_backend import ICameraBackend  # noqa: E402
from edge_camera.infrastructure.backends.basler_camera_backend import (  # noqa: E402
    BaslerCameraBackend,
)


@pytest.fixture(autouse=True)
def reset_mock():
    _mock_camera.reset_mock()
    _mock_grab_result.reset_mock()
    _mock_grab_result.GrabSucceeded.return_value = True
    _mock_grab_result.GetArray.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
    _mock_grab_result.__enter__ = lambda s: s
    _mock_grab_result.__exit__ = MagicMock(return_value=False)
    _mock_camera.RetrieveResult.return_value = _mock_grab_result
    _mock_camera.GetDeviceInfo.return_value = _mock_device_info
    _mock_pylon.InstantCamera.return_value = _mock_camera


@pytest.fixture
def backend():
    return BaslerCameraBackend(serial_number="12345678")


@pytest.fixture
def backend_no_serial():
    return BaslerCameraBackend()


def test_basler_backend_implements_interface(backend):
    assert isinstance(backend, ICameraBackend)


async def test_capture_writes_jpeg_to_output_dir(backend, tmp_path):
    image_ref = await backend.capture(tmp_path, "cam_basler")

    assert image_ref.camera_id == "cam_basler"
    assert image_ref.size_bytes > 0
    assert image_ref.uri.startswith("file://")
    written_path = Path(image_ref.uri.replace("file://", ""))
    assert written_path.exists()
    assert written_path.suffix == ".jpg"


async def test_capture_opens_and_closes_camera(backend, tmp_path):
    await backend.capture(tmp_path, "cam_basler")

    _mock_camera.Open.assert_called_once()
    _mock_camera.Close.assert_called_once()


async def test_capture_multiple_frames_produce_distinct_files(backend, tmp_path):
    ref1 = await backend.capture(tmp_path, "cam_basler")
    await asyncio.sleep(0.01)
    ref2 = await backend.capture(tmp_path, "cam_basler")

    assert ref1.uri != ref2.uri
    assert len(list(tmp_path.glob("*.jpg"))) == 2


def test_health_returns_ok(backend):
    h = backend.health()

    assert h["status"] == "ok"
    assert h["type"] == "basler"
    assert h["serial_number"] == "12345678"


def test_health_returns_error_when_open_raises(backend):
    _mock_camera.Open.side_effect = RuntimeError("device not found")
    try:
        h = backend.health()
        assert h["status"] == "error"
        assert "device not found" in h["error"]
    finally:
        _mock_camera.Open.side_effect = None


def test_metadata_returns_device_info(backend):
    m = backend.metadata()

    assert m["type"] == "basler"
    assert m["serial_number"] == "12345678"
    assert m["model"] == "acA1920-40gc"
    assert m["vendor"] == "Basler"


async def test_start_listening_calls_callback(backend, tmp_path):
    received = []

    async def on_frame(ref):
        received.append(ref)
        if len(received) >= 3:
            raise asyncio.CancelledError

    backend._frame_interval = 0.01
    try:
        await backend.start_listening(tmp_path, "cam_basler", on_frame)
    except asyncio.CancelledError:
        pass

    assert len(received) >= 3
    for ref in received:
        assert ref.camera_id == "cam_basler"


async def test_start_listening_closes_camera_on_cancel(backend, tmp_path):
    async def on_frame(ref):
        raise asyncio.CancelledError

    backend._frame_interval = 0.01
    try:
        await backend.start_listening(tmp_path, "cam_basler", on_frame)
    except asyncio.CancelledError:
        pass

    _mock_camera.Close.assert_called_once()
