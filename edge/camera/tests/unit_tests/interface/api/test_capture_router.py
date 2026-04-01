import pytest
from fastapi.testclient import TestClient

from edge_camera.infrastructure.backends.fake_camera_backend import FakeCameraBackend
from edge_camera.interface.api.app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("CAMERA_OUTPUT_DIR", str(tmp_path))
    a = create_app()
    a.state.backends = {"cam_1": FakeCameraBackend(), "cam_2": FakeCameraBackend()}
    with TestClient(a) as c:
        yield c


def test_capture_single_camera_by_id(client):
    response = client.post("/capture?camera_id=cam_1")

    assert response.status_code == 200
    body = response.json()
    assert body["camera_id"] == "cam_1"
    assert body["uri"].startswith("file://")
    assert body["size_bytes"] > 0
    assert "captured_at" in body


def test_capture_unknown_camera_returns_404(client):
    response = client.post("/capture?camera_id=unknown")

    assert response.status_code == 404


def test_capture_without_camera_id_fails_when_multiple(client):
    response = client.post("/capture")

    assert response.status_code == 400


def test_capture_without_camera_id_succeeds_when_single(tmp_path, monkeypatch):
    monkeypatch.setenv("CAMERA_OUTPUT_DIR", str(tmp_path))
    a = create_app()
    a.state.backends = {"cam_1": FakeCameraBackend()}
    with TestClient(a) as c:
        response = c.post("/capture")
    assert response.status_code == 200
    assert response.json()["camera_id"] == "cam_1"


def test_health_returns_all_cameras(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "cam_1" in body["cameras"]
    assert "cam_2" in body["cameras"]


def test_metadata_returns_all_cameras(client):
    response = client.get("/metadata")

    assert response.status_code == 200
    body = response.json()
    assert "cam_1" in body["cameras"]
    assert body["cameras"]["cam_1"]["type"] == "fake"
