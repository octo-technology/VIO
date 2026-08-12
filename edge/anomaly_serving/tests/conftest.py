"""Test fixtures for anomaly_serving.

The API tests need a *fitted* RAD model, but running a real backbone would pull a
DINOv3 or EUPE download into CI.  Instead a fake backbone is patched in: RAD's
only contact with its encoder is ``extract_multilayer``, so overriding that
method yields a model that exercises the genuine retrieval, scoring, and decision
paths on deterministic synthetic features.
"""

import io
import json
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

# Geometry of the fake backbone: an 8x8 patch grid with 16-dim tokens.
GRID_SIDE = 8
NUM_PATCHES = GRID_SIDE * GRID_SIDE
EMBED_DIM = 16
NUM_REFERENCE_IMAGES = 6

MODEL_NAME = "rad_test_model"
RESIZE = 64
THRESHOLD = 0.5


def _fake_features(images: torch.Tensor, seed: int) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
    """Deterministic stand-in for a frozen backbone's token extraction."""
    generator = torch.Generator().manual_seed(seed)
    batch_size = images.shape[0]
    patches = torch.rand(batch_size, NUM_PATCHES, EMBED_DIM, generator=generator)
    cls = torch.rand(batch_size, EMBED_DIM, generator=generator)
    return [patches], [cls]


@pytest.fixture(scope="session")
def models_dir(tmp_path_factory) -> Path:
    """A MODELS_PATH directory holding one fitted RAD model."""
    from anomaly_serving.rad_model.rad import RAD

    models_path = tmp_path_factory.mktemp("models")
    model_dir = models_path / MODEL_NAME
    model_dir.mkdir()

    # A single-layer model matches the fake backbone's one set of tokens.
    model = RAD(layer_indices=(0,), k_image=3, pos_radius=1, resize_mask=32)
    model.extract_multilayer = lambda images: _fake_features(images, seed=0)  # type: ignore[method-assign]
    model.fit(torch.zeros(NUM_REFERENCE_IMAGES, 3, RESIZE, RESIZE))

    torch.save(
        {
            "hparams": {
                "layer_indices": (0,),
                "k_image": 3,
                "pos_radius": 1,
                "resize_mask": 32,
            },
            "layers": [0],
            "cls_banks": [bank for bank in model.cls_banks],
            "patch_banks": [bank for bank in model.patch_banks],
            "fitted": True,
        },
        model_dir / "model.ckpt",
    )

    metadata = {
        "version": "1",
        "output_type": "anomaly",
        "class_names": ["OK", "KO"],
        "normalization": "imagenet",
        "backbone": "dinov3",
        "layer_indices": [0],
        "resize": RESIZE,
        "k_image": 3,
        "pos_radius": 1,
        "use_positional_bank": True,
        "resize_mask": 32,
        "decision_method": "mean_top_fraction",
        "decision_param": 0.01,
        "threshold": THRESHOLD,
    }
    with (model_dir / "metadata.json").open("w") as f:
        json.dump(metadata, f, indent=2)

    return models_path


@pytest.fixture(scope="session")
def test_client(models_dir: Path):
    """A TestClient whose registry holds the fitted fake-backbone model."""
    from fastapi.testclient import TestClient

    from anomaly_serving.anomaly_server import app
    from anomaly_serving.rad_registry import load_model_metadata, load_rad_model

    model_dir = models_dir / MODEL_NAME
    model = load_rad_model(model_dir / "model.ckpt", load_model_metadata(model_dir))
    # Re-patch after loading: the checkpoint restores the memory bank, but the
    # freshly built RAD instance would otherwise reach for a real encoder.
    model.extract_multilayer = lambda images: _fake_features(images, seed=1)  # type: ignore[method-assign]

    app.state.rad_models = {MODEL_NAME: model}
    app.state.model_metadata = {MODEL_NAME: load_model_metadata(model_dir)}

    with TestClient(app) as client:
        yield client

    app.state.rad_models = None
    app.state.model_metadata = None


@pytest.fixture(scope="session")
def image_bytes() -> bytes:
    """A small JPEG payload, as the orchestrator would POST it."""
    rng = np.random.default_rng(seed=42)
    array = rng.integers(0, 256, size=(128, 128, 3), dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(array).save(buffer, format="JPEG")
    return buffer.getvalue()
