import pytest
import os

from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.infrastructure.model_forward.tf_serving_detection_wrapper import (
    TFServingDetectionWrapper,
)
from tests.conftest import TEST_DATA_FOLDER_PATH


@pytest.mark.asyncio
class TestTFServingDetectionWrapper:
    @pytest.mark.parametrize(
        "setup_test_tensorflow_serving", ["mobilenet_v1_640x640"], indirect=True
    )
    async def test_perform_inference_should_detected_a_cat(self, test_tensorflow_serving_base_url, my_binaries_0):
        # Given
        tf_serving_model_forwarder = TFServingDetectionWrapper(
            base_url=test_tensorflow_serving_base_url,
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_labels"
        )

        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="mobilenet_v1_640x640",
            category="object_detection",
            version="1",
            camera_id="camera_id1",
            boxes_coordinates="detection_boxes",
            objectness_scores="detection_scores",
            number_of_boxes="num_detections",
            detection_classes="detection_classes",
            image_resolution=[640, 640],
            class_to_detect=["cat"],
            class_names_path=os.path.join(
                TEST_DATA_FOLDER_PATH, "test_detection_labels"
            ),
            objectness_threshold=0.5
        )

        expected_model_output = {
            'object_1': {'label': 'cat', 'location': [370, 2, 738, 340], 'score': 0.653498411}
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
            assert round(output["score"], 5) == round(expected_model_output[object_id]["score"], 5)

    @pytest.mark.parametrize(
        "setup_test_tensorflow_serving", ["mobilenet_v1_640x640"], indirect=True
    )
    async def test_perform_inference_should_detected_a_cat_and_a_dog(self, test_tensorflow_serving_base_url,
                                                                     my_binaries_0):  # noqa
        # Given
        tf_serving_model_forwarder = TFServingDetectionWrapper(
            base_url=test_tensorflow_serving_base_url,
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_labels"
        )

        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="mobilenet_v1_640x640",
            category="object_detection",
            version="1",
            camera_id="camera_id2",
            boxes_coordinates="detection_boxes",
            objectness_scores="detection_scores",
            number_of_boxes="num_detections",
            detection_classes="detection_classes",
            image_resolution=[640, 640],
            class_to_detect=["cat", "dog"],
            class_names_path=os.path.join(
                TEST_DATA_FOLDER_PATH, "test_detection_labels"
            ),
            objectness_threshold=0.5
        )

        expected_model_output = {
            'object_1': {'label': 'dog', 'location': [234, 13, 778, 911], 'score': 0.717056394},
            'object_2': {'label': 'cat', 'location': [796, 124, 1371, 935], 'score': 0.682666183}
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
            assert round(output["score"], 5) == round(expected_model_output[object_id]["score"], 5)
