"""Unit tests for incremental memory-bank building and persistence.

A fake backbone stands in for the frozen encoder (see ``conftest``): overriding
``extract_multilayer`` exercises the real append/concat and checkpoint code on
deterministic synthetic features without pulling a model download.
"""

import torch

from anomaly_serving.rad_model.rad import RAD
from anomaly_serving.reference_bank import append_reference_images, save_checkpoint

GRID_SIDE = 8
NUM_PATCHES = GRID_SIDE * GRID_SIDE
EMBED_DIM = 16
RESIZE = 64


def _fake_features(images: torch.Tensor) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
    batch_size = images.shape[0]
    patches = torch.rand(batch_size, NUM_PATCHES, EMBED_DIM)
    cls = torch.rand(batch_size, EMBED_DIM)
    return [patches], [cls]


def _make_model() -> RAD:
    model = RAD(layer_indices=(0,), k_image=3, pos_radius=1, resize_mask=32)
    model.extract_multilayer = lambda images: _fake_features(images)  # type: ignore[method-assign]
    return model


def _images(count: int) -> torch.Tensor:
    return torch.zeros(count, 3, RESIZE, RESIZE)


class TestAppendReferenceImages:
    def test_seeds_the_bank_when_the_model_is_empty(self):
        model = _make_model()
        assert model.cls_banks == []

        bank_size = append_reference_images(model, _images(5))

        assert bank_size == 5
        assert model.cls_banks[-1].shape[0] == 5
        assert model.patch_banks[-1].shape[0] == 5

    def test_appends_to_an_existing_bank(self):
        model = _make_model()
        append_reference_images(model, _images(4))

        bank_size = append_reference_images(model, _images(3))

        assert bank_size == 7
        assert model.cls_banks[-1].shape[0] == 7

    def test_reports_progress_per_batch(self):
        model = _make_model()
        seen: list[int] = []

        append_reference_images(model, _images(20), batch_size=8, progress_cb=seen.append)

        # 20 images in batches of 8 -> cumulative 8, 16, 20.
        assert seen == [8, 16, 20]

    def test_a_model_with_a_bank_can_serve_a_prediction(self):
        model = _make_model()
        append_reference_images(model, _images(6))

        image_scores, anomaly_maps = model.predict(_images(1))

        assert image_scores.shape[0] == 1
        assert anomaly_maps.shape[0] == 1


class TestSaveCheckpoint:
    def test_round_trips_through_the_registry_loader(self, tmp_path):
        from anomaly_serving.rad_registry import load_rad_model

        model = _make_model()
        append_reference_images(model, _images(5))
        ckpt_path = tmp_path / "model.ckpt"

        save_checkpoint(model, ckpt_path)
        reloaded = load_rad_model(ckpt_path, {})

        assert reloaded.cls_banks[-1].shape[0] == 5
        assert torch.equal(reloaded.cls_banks[0], model.cls_banks[0])
        assert torch.equal(reloaded.patch_banks[0], model.patch_banks[0])

    def test_write_is_atomic_leaving_no_temp_file(self, tmp_path):
        model = _make_model()
        append_reference_images(model, _images(2))
        ckpt_path = tmp_path / "model.ckpt"

        save_checkpoint(model, ckpt_path)

        assert ckpt_path.exists()
        assert list(tmp_path.glob("*.tmp")) == []
