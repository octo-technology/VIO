from pathlib import Path
from fastapi.testclient import TestClient
import numpy as np
import io
from PIL import Image

from torch_serving.modelhandler import ModelHandler
from torch_serving.fast_serving import app

class TestFastServing:
    base_url = 'http://localhost:8501'
    test_client = TestClient(app)
    object_detection_model='ols-smart-rack'
    
    
    def test_image_loading_test(self):
        # Given
        image_test_path = Path.cwd() / 'example_images_OLS'/ 'MicrosoftTeams-image (3).png'
        with open(image_test_path, 'rb') as image:
            f = image.read()
            binary_test = bytearray(f)
        
        img_actual = Image.open(io.BytesIO(binary_test))
        im_expected = Image.open(image_test_path)
        
        assert img_actual == im_expected
        
    def test_frame_input(self):
         # Given
        image_test_path = Path.cwd() / 'example_images_OLS'/ 'MicrosoftTeams-image (3).png'
        expected_img = Image.open(image_test_path)
        expected_array = np.asarray(expected_img)
        
        img_test = Image.open(image_test_path)
        array_test = np.asarray(img_test)
        payload = {'inputs': array_test.tolist()}
        expected_array = np.asarray(payload['inputs'])
        
        assert expected_array.shape == expected_array.shape
        np.testing.assert_array_equal(expected_array, expected_array)
        

    def test_serving_return_object_detection_prediction_output_from_image3(self):
        # Given
        image_test_path = Path.cwd() / 'example_images_OLS'/ 'MicrosoftTeams-image (3).png'
        img_test = Image.open(image_test_path)
        array_test = np.asarray(img_test)
        
        expected_json_output = {
            "outputs":
                {
                    "detection_boxes":[[0.05450461432337761,0.5720061659812927,0.12070411443710327,0.6157696843147278]],
                    "detection_classes":[2],
                    "detection_scores":[0.215188130736351]
                 }
        }

        # When
        model_url = f'{self.base_url}/v1/models/{self.object_detection_model}/versions/1'
        payload = {'inputs': array_test.tolist()}
        response = self.test_client.post(f'{model_url}:predict', json=payload)

        # Then
        assert response.json() == expected_json_output
        assert response.status_code == 200
        
    def test_serving_return_object_detection_prediction_output_from_image1(self):
        # Given
        image_test_path = Path.cwd() / 'example_images_OLS'/ 'MicrosoftTeams-image_1.png'
        with open(image_test_path, 'rb') as image:
            f = image.read()
            binary_test = bytearray(f)
        
        img_test = Image.open(io.BytesIO(binary_test))
        array_test = np.asarray(img_test)
        
        expected_json_output = {
            "outputs":
                {
                    "detection_boxes": [[0.0, 0.0, 1.0, 1.0]],
                    "detection_classes":[0],
                    "detection_scores":[0.0]
                 }
        }

        # When
        model_url = f'{self.base_url}/v1/models/{self.object_detection_model}/versions/1'
        payload = {'inputs': array_test.tolist()}
        response = self.test_client.post(f'{model_url}:predict', json=payload)

        # Then
        assert response.json() == expected_json_output
        assert response.status_code == 200
        
    def test_compare_model_handler_fast_serving(self):
        weight_path = Path.cwd() / "trained_models" / "checkpoint_ssd300.pth.tar"
        image_test_path = Path.cwd() / "example_images_OLS" / "MicrosoftTeams-image_1.png"
        img_test = Image.open(image_test_path)
        
        
        model_handler = ModelHandler(checkpoint_pth=weight_path)
        model_handler.load_model(cpu=True)
        model_handler_response = model_handler.handle(data=img_test)
        
        det_boxes, det_labels, det_scores = model_handler_response
        
        # When
        array_test = np.asarray(img_test)
        model_url = f'{self.base_url}/v1/models/{self.object_detection_model}/versions/1'
        payload = {'inputs': array_test.tolist()}
        fast_serving_response = self.test_client.post(f'{model_url}:predict', json=payload)
        
        # Then
        assert fast_serving_response.json()["outputs"]["detection_boxes"] == det_boxes
        
        assert fast_serving_response.json()["outputs"]["detection_classes"] == det_labels
        
        assert fast_serving_response.json()["outputs"]["detection_scores"] == det_scores
