from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.infrastructure.adapters.camera.http_camera import HttpCamera

_FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100


def _make_image_ref(uri: str, camera_id: str = "cam_1") -> dict:
    return {
        "uri": uri,
        "camera_id": camera_id,
        "captured_at": datetime.now().isoformat(),
        "size_bytes": len(_FAKE_JPEG),
    }


@pytest.fixture
def camera_config():
    return CameraConfig(camera_id="cam_1", camera_type=CameraType.HTTP)


@pytest.fixture
def camera(camera_config):
    return HttpCamera(camera_config)


def test_http_camera_implements_interface(camera):
    assert isinstance(camera, ICamera)


def test_capture_reads_file_uri(camera, tmp_path):
    jpeg_path = tmp_path / "cam_1_frame.jpg"
    jpeg_path.write_bytes(_FAKE_JPEG)
    image_ref = _make_image_ref(jpeg_path.as_uri())

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = image_ref

    with patch("httpx.post", return_value=mock_response):
        image = camera.capture()

    assert image.image_bytes == _FAKE_JPEG


def test_capture_posts_to_correct_url_with_camera_id(camera, tmp_path, monkeypatch):
    monkeypatch.setenv("CAMERA_SERVICE_URL", "http://edge-camera:8001")
    cam = HttpCamera(CameraConfig(camera_id="cam_42", camera_type=CameraType.HTTP))

    jpeg_path = tmp_path / "frame.jpg"
    jpeg_path.write_bytes(_FAKE_JPEG)

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = _make_image_ref(jpeg_path.as_uri(), "cam_42")

    with patch("httpx.post", return_value=mock_response) as mock_post:
        cam.capture()

    mock_post.assert_called_once_with(
        "http://edge-camera:8001/capture",
        params={"camera_id": "cam_42"},
        timeout=10.0,
    )


def test_capture_fetches_http_uri(camera):
    http_uri = "http://edge-camera:8001/frames/cam_1_frame.jpg"
    image_ref = _make_image_ref(http_uri)

    mock_post_response = MagicMock()
    mock_post_response.raise_for_status.return_value = None
    mock_post_response.json.return_value = image_ref

    mock_get_response = MagicMock()
    mock_get_response.content = _FAKE_JPEG

    with patch("httpx.post", return_value=mock_post_response):
        with patch("httpx.get", return_value=mock_get_response):
            image = camera.capture()

    assert image.image_bytes == _FAKE_JPEG


def test_capture_raises_on_http_error(camera):
    with patch("httpx.post", side_effect=httpx_http_status_error()):
        with pytest.raises(Exception):
            camera.capture()


def httpx_http_status_error():
    import httpx

    return httpx.HTTPStatusError(
        "404 Not Found",
        request=MagicMock(),
        response=MagicMock(status_code=404),
    )


def test_release_is_noop(camera):
    camera.release()  # must not raise
