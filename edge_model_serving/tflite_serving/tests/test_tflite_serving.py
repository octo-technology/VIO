import os
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient


class TestTfliteServing:
    base_url = 'http://localhost:8501/v1'
    image_test_path = 'tests/data/mask_people_dataset/person_without_mask.jpg'
    binary_test = open(image_test_path, 'rb')
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
        model_url = f'{self.base_url}/models'
        expected_models = ["cellphone_connection_control",
                           "marker_quality_control",
                           "mobilenet_ssd_v2_coco",
                           "mobilenet_ssd_v2_face"]

        # When
        actual_response = self.test_client.get(model_url)

        # Then
        assert actual_response.status_code == 200
        assert sorted(actual_response.json()) == expected_models

    def test_get_model_resolution_should_return_inputs_shape(self):
        # Given
        model_url = f'{self.base_url}/models/cellphone_connection_control/versions/1/resolution'
        expected_resolution = {"inputs_shape": [1, 224, 224, 3]}

        # When
        actual_response = self.test_client.get(model_url)

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == expected_resolution

    def test_serving_return_object_detection_prediction(self):
        # Given
        model_url = f'{self.base_url}/models/mobilenet_ssd_v2_coco/versions/1:predict'

        image_resolution = (300, 300, 3)
        fake_img_array = np.zeros(image_resolution)
        fake_img_preprocessed = np.expand_dims(fake_img_array, axis=0).astype(np.uint8)
        payload = {'inputs': fake_img_preprocessed.tolist()}

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
        model_url = f'{self.base_url}/models/marker_quality_control/versions/1:predict'

        image_resolution = (224, 224, 3)
        fake_img_array = np.zeros(image_resolution)
        fake_img_preprocessed = np.expand_dims(fake_img_array, axis=0).astype(np.uint8)
        payload = {'inputs': fake_img_preprocessed.tolist()}

        expected_prediction = {'outputs': [[0.021249305456876755, 0.9787507057189941]]}

        # When
        actual_response = self.test_client.post(model_url, json=payload)

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == expected_prediction
