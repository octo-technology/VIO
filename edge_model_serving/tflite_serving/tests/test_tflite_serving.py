import io
import os
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image


class TestTfliteServing:
    base_url = "http://localhost:8501/v1"
    image_test_path = "tests/data/mask_people_dataset/person_without_mask.jpg"
    binary_test = open(image_test_path, "rb")
    os.environ["MODELS_PATH"] = (Path.cwd().parent / "models").as_posix()
    from tflite_serving.tflite_server import app

    test_client = TestClient(app)

    def test_get_home_should_return_link_to_docs(self):
        # Given
        expected_message = "tflite-server docs at ip:port/docs"

        # When
        actual_response = self.test_client.get(self.base_url)

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == expected_message

    def test_get_models_should_return_4_models(self):
        # Given
        model_url = f"{self.base_url}/models"
        expected_models = [
            "marker_quality_control",
            "mobilenet_ssd_v2_coco",
            "mobilenet_ssd_v2_face",
            "pin_detection",
            "yolo_coco_nano",
        ]

        # When
        actual_response = self.test_client.get(model_url)

        # Then
        assert actual_response.status_code == 200
        assert expected_models == sorted(actual_response.json())

    def test_get_model_resolution_should_return_inputs_shape(self):
        # Given
        model_url = (
            f"{self.base_url}/models/mobilenet_ssd_v2_coco/versions/1/resolution"
        )
        expected_resolution = {"inputs_shape": [1, 300, 300, 3]}

        # When
        actual_response = self.test_client.get(model_url)

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == expected_resolution

    def test_serving_return_object_detection_prediction(self):
        # Given
        model_url = f"{self.base_url}/models/mobilenet_ssd_v2_coco/versions/1:predict"

        image_resolution = (300, 300, 3)
        fake_img_array = np.zeros(image_resolution)
        fake_img_preprocessed = np.expand_dims(fake_img_array, axis=0).astype(np.uint8)
        payload = {"inputs": fake_img_preprocessed.tolist()}

        # When
        actual_response = self.test_client.post(model_url, json=payload)

        # Then
        assert actual_response.status_code == 200
        actual_prediction = actual_response.json()
        assert "detection_boxes" in actual_prediction["outputs"]
        assert isinstance(actual_prediction["outputs"]["detection_boxes"], list)
        assert "detection_classes" in actual_prediction["outputs"]
        assert isinstance(actual_prediction["outputs"]["detection_classes"], list)
        assert "detection_scores" in actual_prediction["outputs"]
        assert isinstance(actual_prediction["outputs"]["detection_scores"], list)

    def test_serving_return_classification_prediction(self):
        # Given
        model_url = f"{self.base_url}/models/marker_quality_control/versions/1:predict"

        image_resolution = (224, 224, 3)
        fake_img_array = np.zeros(image_resolution)
        fake_img_preprocessed = np.expand_dims(fake_img_array, axis=0).astype(np.uint8)
        payload = {"inputs": fake_img_preprocessed.tolist()}

        expected_prediction = {"outputs": [[0.02125023491680622, 0.9787498116493225]]}

        # When
        actual_response = self.test_client.post(model_url, json=payload)

        # Then
        assert actual_response.status_code == 200
        for elements in actual_response.json()["outputs"]:
            for index_value, value in enumerate(elements):
                assert round(value, 6) == round(
                    expected_prediction["outputs"][0][index_value], 6
                )

    def test_serving_for_yolo_detection_model_runs(self):
        # Given
        model_url = f"{self.base_url}/models/yolo_coco_nano/versions/1:predict"
        with open(self.image_test_path, "rb") as image_file:
            image = Image.open(io.BytesIO(image_file.read()))
            resized_image = image.resize((320, 320), Image.ANTIALIAS)
            img = np.expand_dims(resized_image, axis=0).astype(np.uint8)

        payload = {"inputs": img.tolist(), "model_type": "yolo"}

        # When
        actual_response = self.test_client.post(model_url, json=payload)

        # Then
        assert actual_response.status_code == 200
