from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.infrastructure.model_forward.tf_serving_detection_wrapper import (
    TFServingDetectionWrapper,
)
from tests.conftest import TEST_DATA_FOLDER_PATH


class TestDetectionWrapperHelper:
    def test_perform_pre_processing_should_return_an_image_as_an_array_with_the_expected_format(
        self,
    ):
        # Given
        model_forwarder = TFServingDetectionWrapper(
            base_url="",
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_labels",
        )
        binary = open(TEST_DATA_FOLDER_PATH / "mask_images" / "person_with_mask.jpg", "br").read()
        expected_shape = (1, 720, 1080, 3)

        model = ModelInfos(
            "id1",
            "name1",
            "object_detection",
            "1",
            "camera_id1",
            image_resolution=[1080, 720],
        )

        # When
        actual = model_forwarder.perform_pre_processing(model, binary)

        # Then
        assert actual.shape == expected_shape
        assert 0 <= actual.min() <= 255
        assert 0 <= actual.max() <= 255

    def test_perform_post_processing_should_transform_the_standard_output_from_the_model_into_the_expected_format(
        self,
    ):
        # Given
        model_forwarder = TFServingDetectionWrapper(
            base_url="",
            class_names_path=TEST_DATA_FOLDER_PATH / "test_detection_foo_bar_baz_labels",
            image_shape=[1, 1],
        )
        json_outputs = {
            "detection_boxes": [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]],
            "detection_scores": [[0.8, 0.7, 0.6]],
            "detection_classes": [[1.0, 1.0, 2.0]],
        }

        model = ModelInfos(
            "id1",
            "name1",
            "detection",
            "1",
            "camera_id1",
            image_resolution=[640, 640],
            model_type="Mobilenet",
            class_names=["foo", "bar", "baz"],
            detection_boxes="detection_boxes",
            detection_scores="detection_scores",
            number_of_boxes="num_detections",
            detection_classes="detection_classes",
            class_to_detect=["foo"],
            objectness_threshold=0.5,
        )

        expected = {
            "object_1": {"label": "foo", "location": [2, 1, 4, 3], "score": 0.8},
            "object_2": {"label": "foo", "location": [6, 5, 8, 7], "score": 0.7},
        }

        # When
        actual = model_forwarder.perform_post_processing(model, json_outputs)

        # Then
        assert actual == expected
