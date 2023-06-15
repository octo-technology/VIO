import os
import requests
import json
from pathlib import Path

import numpy as np


class TestTorchServing:
    base_url = "http://localhost:8080/ping"
    image_test_path = 'data/mask_people_dataset/person_without_mask.jpg'
    binary_test = open(image_test_path, 'rb')
    os.environ["MODELS_PATH"] = (Path.cwd().parent / "models").as_posix()

    def test_get_ping_should_return_healthy_status(self):
        # Given
        expected_message = json.loads('{"status": "Healthy"}')

        # When
        actual_response = requests.get(self.base_url)

        # Then
        assert actual_response.status_code == 200
        assert actual_response.json() == expected_message
