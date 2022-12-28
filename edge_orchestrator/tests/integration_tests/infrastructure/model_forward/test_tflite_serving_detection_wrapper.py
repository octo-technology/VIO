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
        "setup_test_tflite_serving", ["mobilenet_ssd_v2_coco"], indirect=True
    )
    async def test_perform_inference_should_detect_a_bear(
            self, test_tflite_serving_base_url, my_binaries_0
    ):
        # Given
        tf_serving_model_forwarder = TFServingDetectionWrapper(
            base_url=test_tflite_serving_base_url,
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_labels"
        )

        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="mobilenet_ssd_v2_coco",
            category="object_detection",
            version="1",
            camera_id="camera_id1",
            boxes_coordinates="detection_boxes",
            objectness_scores="detection_scores",
            number_of_boxes="num_detections",
            detection_classes="detection_classes",
            image_resolution=[300, 300],
            class_to_detect=["bear"],
            class_names_path=os.path.join(
                TEST_DATA_FOLDER_PATH, "test_detection_labels"
            ),
            objectness_threshold=0.5
        )

        expected_model_output = {
            'object_1': {'label': 'bear', 'location': [383, 4, 723, 339], 'score': 0.83984375}
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
        "setup_test_tflite_serving", ["mobilenet_ssd_v2_coco"], indirect=True
    )
    async def test_perform_inference_should_detect_a_cat_and_a_dog(
            self, test_tflite_serving_base_url, my_binaries_0
    ):
        # Given
        tf_serving_model_forwarder = TFServingDetectionWrapper(
            base_url=test_tflite_serving_base_url,
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_labels"
        )

        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="mobilenet_ssd_v2_coco",
            category="object_detection",
            version="1",
            camera_id="camera_id2",
            boxes_coordinates="detection_boxes",
            objectness_scores="detection_scores",
            number_of_boxes="num_detections",
            detection_classes="detection_classes",
            image_resolution=[300, 300],
            class_to_detect=["cat", "dog"],
            class_names_path=os.path.join(
                TEST_DATA_FOLDER_PATH, "test_detection_labels"
            ),
            objectness_threshold=0.5
        )

        expected_model_output = {
            'object_1': {'label': 'cat', 'location': [774, 132, 1377, 946], 'score': 0.93359375},
            'object_2': {'label': 'dog', 'location': [225, 6, 796, 915], 'score': 0.91015625}
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
