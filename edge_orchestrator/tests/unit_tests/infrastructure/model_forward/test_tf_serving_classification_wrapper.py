from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.infrastructure.model_forward.tf_serving_classification_wrapper import (
    TFServingClassificationWrapper,
)
from tests.conftest import TEST_DATA_FOLDER_PATH


class TestClassifModelHelper:
    def test_perform_pre_processing_should_return_an_image_as_an_array_with_the_expected_format(
        self,
    ):
        # Given
        model_forwarder = TFServingClassificationWrapper(base_url="")
        binary = open(TEST_DATA_FOLDER_PATH / "mask_images" / "person_with_mask.jpg", "br").read()
        expected_shape = (1, 224, 224, 3)

        model = ModelInfos(
            "id1",
            "name1",
            "classification",
            "1",
            "camera_id1",
            image_resolution=[224, 224],
        )

        # When
        actual = model_forwarder.perform_pre_processing(model, binary)

        # Then
        assert actual.shape == expected_shape

    def test_perform_post_processing_should_transform_the_standard_output_from_the_model_into_the_expected_format(
        self,
    ):
        # Given
        model_forwarder = TFServingClassificationWrapper(base_url="")

        model = ModelInfos(
            "id1",
            "name1",
            "classification",
            "1",
            "camera_id1",
            image_resolution=[224, 224],
            class_names=["OK", "KO"],
        )

        json_outputs = [[0.1, 0.9]]

        expected = {"binary1": {"label": "KO", "probability": 0.9}}

        # When
        actual = model_forwarder.perform_post_processing(model, json_outputs, "binary1")

        # Then
        assert actual == expected
