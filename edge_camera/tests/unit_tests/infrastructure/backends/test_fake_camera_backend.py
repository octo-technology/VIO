import asyncio
from pathlib import Path

import pytest

from edge_camera.domain.ports.i_camera_backend import ICameraBackend
from edge_camera.infrastructure.backends.fake_camera_backend import FakeCameraBackend


@pytest.fixture
def backend():
    return FakeCameraBackend()


def test_fake_camera_implements_interface(backend):
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
    output_dir = tmp_path / "cam_1"
    await backend.capture(output_dir, "cam_1")

    assert output_dir.exists()
    assert len(list(output_dir.glob("*.jpg"))) == 1


async def test_capture_multiple_frames_produce_distinct_files(backend, tmp_path):
    ref1 = await backend.capture(tmp_path, "cam_1")
    await asyncio.sleep(0.01)
    ref2 = await backend.capture(tmp_path, "cam_1")

    assert ref1.uri != ref2.uri
    assert len(list(tmp_path.glob("*.jpg"))) == 2


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


def test_health_returns_ok(backend):
    h = backend.health()
    assert h["status"] == "ok"
    assert h["type"] == "fake"


def test_metadata_returns_resolution(backend):
    m = backend.metadata()
    assert "resolution" in m
    assert m["type"] == "fake"
