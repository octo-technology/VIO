from fastapi.testclient import TestClient
from edge_tflite_serving.tflite_server import app
import numpy as np


class TestTfliteServing:
    base_url = 'http://localhost:8501'
    image_test_path = 'tests/data/mask_people_dataset/person_without_mask.jpg'
    binary_test = open(image_test_path, 'rb')
    test_client = TestClient(app)

    def test_serving_return_object_detection_prediction(self):
        # Given
        object_detection_model = 'mobilenet_ssd_v2_coco'
        image_resolution = (300, 300, 3)
        model_url = f'{self.base_url}/v1/models/{object_detection_model}/versions/1'
        fake_img_array = np.zeros(image_resolution)
        fake_img_preprocessed = np.expand_dims(fake_img_array, axis=0).astype(np.uint8)
        payload = {'inputs': fake_img_preprocessed.tolist()}

        # When
        response = self.test_client.post(f'{model_url}:predict', json=payload)

        # Then
        assert response.status_code == 200

    def test_serving_return_classification_prediction(self):
        # Given
        classification_model = 'marker_quality_control'
        image_resolution = (224, 224, 3)
        model_url = f'{self.base_url}/v1/models/{classification_model}/versions/1'
        fake_img_array = np.zeros(image_resolution)
        fake_img_preprocessed = np.expand_dims(fake_img_array, axis=0).astype(np.uint8)
        payload = {'inputs': fake_img_preprocessed.tolist()}

        # When
        response = self.test_client.post(f'{model_url}:predict', json=payload)

        # Then
        assert response.status_code == 200
