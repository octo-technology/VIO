"""API tests for the reference-image fit endpoints and their progress polling.

Uses a function-scoped client with its own fake-backbone model and a temporary
``MODELS_PATH`` so each test's fit and the checkpoint it writes stay isolated.
"""

import io
import json

import numpy as np
import pytest
import torch
from fastapi.testclient import TestClient
from PIL import Image

from anomaly_serving.anomaly_server import app
from anomaly_serving.rad_model.rad import RAD

MODEL_NAME = "fit_test_model"
RESIZE = 64
NUM_PATCHES = 64
EMBED_DIM = 16
INITIAL_BANK = 3


def _fake_features(images: torch.Tensor) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
    batch_size = images.shape[0]
    return [torch.rand(batch_size, NUM_PATCHES, EMBED_DIM)], [torch.rand(batch_size, EMBED_DIM)]


def _jpeg_bytes(seed: int = 0) -> bytes:
    rng = np.random.default_rng(seed=seed)
    array = rng.integers(0, 256, size=(96, 96, 3), dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(array).save(buffer, format="JPEG")
    return buffer.getvalue()


def _upload_files(count: int) -> list[tuple[str, tuple[str, bytes, str]]]:
    return [("files", (f"normal_{i}.jpg", _jpeg_bytes(i), "image/jpeg")) for i in range(count)]


@pytest.fixture
def fit_client(tmp_path, monkeypatch):
    monkeypatch.setenv("MODELS_PATH", str(tmp_path))
    model_dir = tmp_path / MODEL_NAME
    model_dir.mkdir()
    metadata = {
        "version": "1",
        "output_type": "anomaly",
        "class_names": ["OK", "KO"],
        "backbone": "dinov3",
        "layer_indices": [0],
        "resize": RESIZE,
        "decision_method": "mean_top_fraction",
        "decision_param": 0.01,
        "threshold": 0.5,
    }
    (model_dir / "metadata.json").write_text(json.dumps(metadata))

    model = RAD(layer_indices=(0,), k_image=3, pos_radius=1, resize_mask=32)
    model.extract_multilayer = lambda images: _fake_features(images)  # type: ignore[method-assign]
    model.fit(torch.zeros(INITIAL_BANK, 3, RESIZE, RESIZE))

    app.state.rad_models = {MODEL_NAME: model}
    app.state.model_metadata = {MODEL_NAME: metadata}
    app.state.fit_jobs = {}
    app.state.fitting_models = set()

    with TestClient(app) as client:
        yield client, model, tmp_path

    app.state.rad_models = None
    app.state.model_metadata = None
    app.state.fit_jobs = {}
    app.state.fitting_models = set()


def _wait_for_job(client: TestClient, url: str, timeout_polls: int = 200) -> dict:
    """Poll a fit job until it leaves the running/pending states."""
    for _ in range(timeout_polls):
        body = client.get(url).json()
        if body["status"] in ("completed", "failed"):
            return body
    raise AssertionError(f"fit job did not finish within {timeout_polls} polls: {body}")


class TestAddReferenceImages:
    def test_accepts_images_and_reports_completion_with_progress(self, fit_client):
        client, model, tmp_path = fit_client

        response = client.post(f"/v1/models/{MODEL_NAME}/reference-images", files=_upload_files(4))

        assert response.status_code == 202
        accepted = response.json()
        assert accepted["total"] == 4
        assert accepted["status"] == "pending"

        job_url = f"/v1/models/{MODEL_NAME}/reference-images/jobs/{accepted['job_id']}"
        final = _wait_for_job(client, job_url)

        assert final["status"] == "completed"
        assert final["processed"] == 4
        assert final["total"] == 4
        assert final["bank_size"] == INITIAL_BANK + 4

    def test_persists_the_bank_to_disk_for_fast_reboot(self, fit_client):
        client, model, tmp_path = fit_client

        response = client.post(f"/v1/models/{MODEL_NAME}/reference-images", files=_upload_files(2))
        job_url = f"/v1/models/{MODEL_NAME}/reference-images/jobs/{response.json()['job_id']}"
        _wait_for_job(client, job_url)

        ckpt_path = tmp_path / MODEL_NAME / "model.ckpt"
        assert ckpt_path.exists()

        from anomaly_serving.rad_registry import load_rad_model

        reloaded = load_rad_model(ckpt_path, {})
        assert reloaded.cls_banks[-1].shape[0] == INITIAL_BANK + 2

    def test_grows_the_live_model_bank_in_place(self, fit_client):
        client, model, tmp_path = fit_client

        response = client.post(f"/v1/models/{MODEL_NAME}/reference-images", files=_upload_files(5))
        job_url = f"/v1/models/{MODEL_NAME}/reference-images/jobs/{response.json()['job_id']}"
        _wait_for_job(client, job_url)

        # Same object the registry serves predictions from — usable without a restart.
        assert model.cls_banks[-1].shape[0] == INITIAL_BANK + 5

    def test_returns_404_for_an_unknown_model(self, fit_client):
        client, _, _ = fit_client
        response = client.post("/v1/models/nope/reference-images", files=_upload_files(1))
        assert response.status_code == 404

    def test_returns_400_when_no_images_are_provided(self, fit_client):
        client, _, _ = fit_client
        response = client.post(f"/v1/models/{MODEL_NAME}/reference-images", files=[])
        assert response.status_code == 400

    def test_returns_409_when_a_fit_is_already_running(self, fit_client):
        client, _, _ = fit_client
        app.state.fitting_models.add(MODEL_NAME)
        response = client.post(f"/v1/models/{MODEL_NAME}/reference-images", files=_upload_files(1))
        assert response.status_code == 409


class TestGetFitJob:
    def test_returns_404_for_an_unknown_job(self, fit_client):
        client, _, _ = fit_client
        response = client.get(f"/v1/models/{MODEL_NAME}/reference-images/jobs/does-not-exist")
        assert response.status_code == 404
