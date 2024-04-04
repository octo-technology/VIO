import os

import pytest

from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.infrastructure.model_forward.tf_serving_detection_wrapper import (
    TFServingDetectionWrapper,
)
from tests.conftest import TEST_DATA_FOLDER_PATH


@pytest.mark.asyncio
class TestTFServingDetectionWrapper:
    @pytest.mark.parametrize(
        "setup_test_tflite_serving", ["mobilenet_ssd_v2_coco"], indirect=True
    )
    async def test_perform_inference_should_detect_a_bear(
        self, test_tflite_serving_base_url, my_binaries_0
    ):
        # Given
        tf_serving_model_forwarder = TFServingDetectionWrapper(
            base_url=test_tflite_serving_base_url,
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_labels",
        )

        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="mobilenet_ssd_v2_coco",
            category="object_detection",
            model_type="Mobilenet",
            version="1",
            camera_id="camera_id1",
            detection_boxes="detection_boxes",
            detection_scores="detection_scores",
            number_of_boxes="num_detections",
            detection_classes="detection_classes",
            image_resolution=[300, 300],
            class_to_detect=["bear"],
            class_names_path=os.path.join(
                TEST_DATA_FOLDER_PATH, "test_detection_labels"
            ),
            objectness_threshold=0.5,
        )

        expected_model_output = {
            "object_1": {
                "label": "bear",
                "location": [0.4008, 0.0124, 0.7688, 0.9982],
                "score": 0.87890625,
            }
        }

        # When
        actual_model_output = await tf_serving_model_forwarder.perform_inference(
            model_inference_version, my_binaries_0["camera_id1"], ""
        )

        # Then
        assert actual_model_output.keys() == expected_model_output.keys()
        for object_id, output in actual_model_output.items():
            assert output["label"] == expected_model_output[object_id]["label"]
            assert output["location"] == expected_model_output[object_id]["location"]
            assert round(output["score"], 5) == round(
                expected_model_output[object_id]["score"], 5
            )

    @pytest.mark.parametrize(
        "setup_test_tflite_serving", ["mobilenet_ssd_v2_coco"], indirect=True
    )
    async def test_perform_inference_should_detect_a_cat_and_a_dog(
        self, test_tflite_serving_base_url, my_binaries_0
    ):
        # Given
        tf_serving_model_forwarder = TFServingDetectionWrapper(
            base_url=test_tflite_serving_base_url,
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_labels",
        )

        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="mobilenet_ssd_v2_coco",
            category="object_detection",
            model_type="Mobilenet",
            version="1",
            camera_id="camera_id2",
            detection_boxes="detection_boxes",
            detection_scores="detection_scores",
            number_of_boxes="num_detections",
            detection_classes="detection_classes",
            image_resolution=[300, 300],
            class_to_detect=["cat", "dog"],
            class_names_path=os.path.join(
                TEST_DATA_FOLDER_PATH, "test_detection_labels"
            ),
            objectness_threshold=0.5,
        )

        expected_model_output = {
            "object_1": {
                "label": "cat",
                "location": [0.4643, 0.1408, 0.8258, 1.0086],
                "score": 0.93359375,
            },
            "object_2": {
                "label": "dog",
                "location": [0.1355, 0.0072, 0.4777, 0.9755],
                "score": 0.91015625,
            },
        }

        # When
        actual_model_output = await tf_serving_model_forwarder.perform_inference(
            model_inference_version, my_binaries_0["camera_id2"], ""
        )

        # Then
        assert actual_model_output.keys() == expected_model_output.keys()
        for object_id, output in actual_model_output.items():
            assert output["label"] == expected_model_output[object_id]["label"]
            assert output["location"] == expected_model_output[object_id]["location"]
            assert round(output["score"], 5) == round(
                expected_model_output[object_id]["score"], 5
            )

    @pytest.mark.parametrize(
        "setup_test_tflite_serving", ["yolo_coco_nano"], indirect=True
    )
    async def test_perform_with_yolo_inference_should_detect_a_giraffe_zebra_and_elephant(
        self, test_tflite_serving_base_url, my_binaries_2
    ):
        # Given
        tf_serving_model_forwarder = TFServingDetectionWrapper(
            base_url=test_tflite_serving_base_url,
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_labels_yolo",
        )

        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="yolo_coco_nano",
            category="object_detection",
            model_type="yolo",
            version="1",
            camera_id="camera_id4",
            detection_boxes="detection_boxes",
            detection_scores="detection_scores",
            class_names_path=os.path.join(
                TEST_DATA_FOLDER_PATH, "test_detection_labels_yolo"
            ),
            detection_classes="detection_classes",
            image_resolution=[320, 320],
            objectness_threshold=0.5,
        )

        expected_model_output = {
            "object_1": {
                "label": "giraffe",
                "location": [0.1633, 0.1537, 0.4971, 0.9183],
                "score": 0.94316,
                "metadata": None,
            },
            "object_2": {
                "label": "zebra",
                "location": [0.0342, 0.7625, 0.2051, 0.9359],
                "score": 0.92974,
                "metadata": None,
            },
            "object_3": {
                "label": "elephant",
                "location": [0.9241, 0.5623, 0.9793, 0.6468],
                "score": 0.62438,
                "metadata": None,
            },
        }

        # When
        actual_model_output = await tf_serving_model_forwarder.perform_inference(
            model_inference_version, my_binaries_2["camera_id3"], ""
        )

        # Then
        assert actual_model_output.keys() == expected_model_output.keys()
        for object_id, output in actual_model_output.items():
            assert output["label"] == expected_model_output[object_id]["label"]
            assert output["location"] == expected_model_output[object_id]["location"]
            assert round(output["score"], 5) == round(
                expected_model_output[object_id]["score"], 5
            )
