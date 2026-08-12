"""API tests for anomaly_serving.

These mirror ``tflite_serving``'s integration tests: the contract must stay
identical so the orchestrator can point a pipeline step at either service.
"""

import torch

from anomaly_serving.rad_registry import warm_up
from tests.conftest import MODEL_NAME, RESIZE, THRESHOLD

BASE_URL = "http://localhost:8502/v1"


class TestWarmUp:
    def test_warm_up_runs_a_prediction_without_raising(self, models_dir):
        # Given a freshly loaded model that has never predicted
        from anomaly_serving.rad_registry import load_model_metadata, load_rad_model
        from tests.conftest import _fake_features

        model_dir = models_dir / MODEL_NAME
        model = load_rad_model(model_dir / "model.ckpt", load_model_metadata(model_dir))
        model.extract_multilayer = lambda images: _fake_features(images, seed=2)  # type: ignore[method-assign]
        assert model._bank_device is None

        # When
        warm_up(model, RESIZE)

        # Then the on-device banks are materialised, so the next call skips that work
        assert model._bank_device is not None

    def test_warm_up_accepts_the_configured_resize(self, models_dir):
        # Given
        from anomaly_serving.rad_registry import load_model_metadata, load_rad_model
        from tests.conftest import _fake_features

        model_dir = models_dir / MODEL_NAME
        model = load_rad_model(model_dir / "model.ckpt", load_model_metadata(model_dir))
        captured = {}

        def _capture(images: torch.Tensor):
            captured["shape"] = tuple(images.shape)
            return _fake_features(images, seed=3)

        model.extract_multilayer = _capture  # type: ignore[method-assign]

        # When
        warm_up(model, RESIZE)

        # Then a single image of the configured size was pushed through
        assert captured["shape"] == (1, 3, RESIZE, RESIZE)


class TestInfo:
    def test_get_home_should_return_link_to_docs(self, test_client):
        # When
        actual_response = test_client.get(BASE_URL)

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == "rad-server docs at ip:port/docs"


class TestModels:
    def test_get_models_should_return_all_loaded_models(self, test_client):
        # When
        actual_response = test_client.get(f"{BASE_URL}/models")

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == [MODEL_NAME]

    def test_get_capabilities_returns_output_type_and_class_names(self, test_client):
        # When
        actual_response = test_client.get(f"{BASE_URL}/capabilities")

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == {
            "models": {
                MODEL_NAME: {
                    "version": "1",
                    "output_type": "anomaly",
                    "class_names": ["OK", "KO"],
                }
            }
        }


class TestModelMetadata:
    def test_get_model_metadata_returns_shape_and_rad_specific_fields(self, test_client):
        # When
        actual_response = test_client.get(f"{BASE_URL}/models/{MODEL_NAME}/metadata")

        # Then
        assert actual_response.status_code == 200
        data = actual_response.json()
        assert data["input_shape"] == [1, RESIZE, RESIZE, 3]
        assert data["input_dtype"] == "uint8"
        assert data["output_type"] == "anomaly"
        assert data["class_names"] == ["OK", "KO"]
        assert data["backbone"] == "dinov3"
        assert data["resize"] == RESIZE
        assert data["decision_method"] == "mean_top_fraction"
        assert data["decision_param"] == 0.01
        assert data["threshold"] == THRESHOLD

    def test_get_model_metadata_returns_404_for_unknown_model(self, test_client):
        # When
        actual_response = test_client.get(f"{BASE_URL}/models/unknown_model/metadata")

        # Then
        assert actual_response.status_code == 404


class TestPredict:
    def test_predict_returns_anomaly_prediction(self, test_client, image_bytes):
        # When
        actual_response = test_client.post(
            f"{BASE_URL}/models/{MODEL_NAME}/versions/1:predict",
            content=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 200
        data = actual_response.json()
        assert data["label"] in ["OK", "KO"]
        assert 0.0 <= data["probability"] <= 1.0
        assert isinstance(data["raw_score"], float)
        assert data["decision_method"] == "mean_top_fraction"
        assert data["decision_param"] == 0.01
        assert data["threshold"] == THRESHOLD

    def test_predict_reuses_the_class_discriminator_the_orchestrator_parses(self, test_client, image_bytes):
        # The orchestrator's ModelForwarder dispatches on prediction_type and
        # reads label/probability; anything else here breaks pipeline wiring.
        # When
        actual_response = test_client.post(
            f"{BASE_URL}/models/{MODEL_NAME}/versions/1:predict",
            content=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        data = actual_response.json()
        assert data["prediction_type"] == "class"
        assert set(["prediction_type", "label", "probability"]).issubset(data)

    def test_predict_label_agrees_with_score_and_threshold(self, test_client, image_bytes):
        # When
        actual_response = test_client.post(
            f"{BASE_URL}/models/{MODEL_NAME}/versions/1:predict",
            content=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        data = actual_response.json()
        expected_label = "KO" if data["raw_score"] >= data["threshold"] else "OK"
        assert data["label"] == expected_label

    def test_predict_returns_400_for_empty_body(self, test_client):
        # When
        actual_response = test_client.post(
            f"{BASE_URL}/models/{MODEL_NAME}/versions/1:predict",
            content=b"",
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 400

    def test_predict_returns_404_for_unknown_model(self, test_client, image_bytes):
        # When
        actual_response = test_client.post(
            f"{BASE_URL}/models/unknown_model/versions/1:predict",
            content=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 404

    def test_predict_returns_500_for_a_body_that_is_not_an_image(self, test_client):
        # When
        actual_response = test_client.post(
            f"{BASE_URL}/models/{MODEL_NAME}/versions/1:predict",
            content=b"this is not an image",
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 500
