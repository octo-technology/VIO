import os
from pathlib import Path

from fastapi.testclient import TestClient


class TestTfliteServing:
    base_url = "http://localhost:8501/v1"
    image_test_path = "tests/data/mask_people_dataset/person_without_mask.jpg"
    os.environ["MODELS_PATH"] = (Path.cwd().parent / "models").as_posix()
    from tflite_serving.tflite_server import app

    test_client = TestClient(app)

    def _image_bytes(self) -> bytes:
        with open(self.image_test_path, "rb") as f:
            return f.read()

    # ------------------------------------------------------------------
    # GET /v1/
    # ------------------------------------------------------------------

    def test_get_home_should_return_link_to_docs(self):
        # When
        actual_response = self.test_client.get(self.base_url)

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == "tflite-server docs at ip:port/docs"

    # ------------------------------------------------------------------
    # GET /v1/models
    # ------------------------------------------------------------------

    def test_get_models_should_return_all_loaded_models(self):
        # Given
        expected_models = [
            "marker_quality_control",
            "mobilenet_ssd_v2_coco",
            "mobilenet_ssd_v2_face",
            "pin_detection",
            "yolo_coco_nano",
        ]

        # When
        actual_response = self.test_client.get(f"{self.base_url}/models")

        # Then
        assert actual_response.status_code == 200
        assert expected_models == sorted(actual_response.json())

    # ------------------------------------------------------------------
    # GET /v1/models/{model_name}/metadata
    # ------------------------------------------------------------------

    def test_get_model_metadata_returns_shape_and_metadata_for_classification_model(
        self,
    ):
        # When
        actual_response = self.test_client.get(
            f"{self.base_url}/models/marker_quality_control/metadata"
        )

        # Then
        assert actual_response.status_code == 200
        data = actual_response.json()
        assert data["input_shape"] == [1, 224, 224, 3]
        assert data["output_type"] == "classification"
        assert data["class_names"] == ["OK", "KO"]
        assert data["normalization"] == "mobilenet"

    def test_get_model_metadata_returns_shape_and_metadata_for_detection_model(self):
        # When
        actual_response = self.test_client.get(
            f"{self.base_url}/models/mobilenet_ssd_v2_coco/metadata"
        )

        # Then
        assert actual_response.status_code == 200
        data = actual_response.json()
        assert data["input_shape"] == [1, 300, 300, 3]
        assert data["output_type"] == "object_detection"
        assert data["normalization"] == "uint8"

    def test_get_model_metadata_returns_404_for_unknown_model(self):
        # When
        actual_response = self.test_client.get(
            f"{self.base_url}/models/unknown_model/metadata"
        )

        # Then
        assert actual_response.status_code == 404

    # ------------------------------------------------------------------
    # POST /v1/models/{model_name}/versions/{version}:predict
    # ------------------------------------------------------------------

    def test_predict_classification_model_returns_typed_prediction(self):
        # Given
        image_bytes = self._image_bytes()

        # When
        actual_response = self.test_client.post(
            f"{self.base_url}/models/marker_quality_control/versions/1:predict",
            data=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 200
        data = actual_response.json()
        assert data["prediction_type"] == "class"
        assert data["label"] in ["OK", "KO"]
        assert 0.0 <= data["probability"] <= 1.0

    def test_predict_object_detection_model_returns_typed_prediction(self):
        # Given
        image_bytes = self._image_bytes()

        # When
        actual_response = self.test_client.post(
            f"{self.base_url}/models/mobilenet_ssd_v2_coco/versions/1:predict",
            data=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 200
        data = actual_response.json()
        assert data["prediction_type"] == "objects"
        assert "detected_objects" in data
        obj = data["detected_objects"]["object_1"]
        assert "location" in obj and "objectness" in obj and "label" in obj

    def test_predict_yolo_model_returns_typed_prediction(self):
        # Given
        image_bytes = self._image_bytes()

        # When
        actual_response = self.test_client.post(
            f"{self.base_url}/models/yolo_coco_nano/versions/1:predict",
            data=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 200
        data = actual_response.json()
        assert data["prediction_type"] == "objects"

    def test_predict_returns_400_for_empty_body(self):
        # When
        actual_response = self.test_client.post(
            f"{self.base_url}/models/marker_quality_control/versions/1:predict",
            data=b"",
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 400

    def test_predict_returns_404_for_unknown_model(self):
        # Given
        image_bytes = self._image_bytes()

        # When
        actual_response = self.test_client.post(
            f"{self.base_url}/models/unknown_model/versions/1:predict",
            data=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        # Then
        assert actual_response.status_code == 404
