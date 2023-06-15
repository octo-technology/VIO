import os
from pathlib import Path
import torch
import numpy as np
from torchserve_handler import convert_box_definition


class TestTorchServeHandler:
    image_test_path = 'tests/data/mask_people_dataset/person_without_mask.jpg'
    binary_test = open(image_test_path, 'rb')
    os.environ["MODELS_PATH"] = (Path.cwd().parent / "models").as_posix()

    def test_send_box_as_xywh_should_return_it_as_x1y1x2x2(self):
        # Given
        inference = torch.Tensor([
            [460.5378, 304.3144,  40.5174,  29.5539]])
            # [460.5346, 304.2960,  39.7271,  28.7515]])
        expected_box = torch.Tensor([[440.2791, 289.5374, 480.7965, 319.0913]])
            # [440.6711, 289.9202, 480.3982, 318.6718]])
        # When
        actual_response = convert_box_definition(inference)

        # Then
        assert torch.equal(actual_response, expected_box)

