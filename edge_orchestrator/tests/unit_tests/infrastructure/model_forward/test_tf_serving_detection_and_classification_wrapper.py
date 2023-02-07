from edge_orchestrator.infrastructure.model_forward.tf_serving_detection_and_classification_wrapper import \
    TFServingDetectionClassificationWrapper
from edge_orchestrator.domain.models.model_infos import ModelInfos
from tests.conftest import TEST_DATA_FOLDER_PATH


class TestDetectionClassificationHelper:
    def test_perform_pre_processing_should_return_an_image_as_an_array_with_the_expected_format(self):
        # Given
        model_forwarder = TFServingDetectionClassificationWrapper(
            base_url='',
            class_names_path=TEST_DATA_FOLDER_PATH / 'test_detection_labels'
        )
        binary = open(TEST_DATA_FOLDER_PATH / 'mask_images' / 'person_with_mask.jpg', 'br').read()
        expected_shape = (1, 720, 1080, 3)

        # When
        actual = model_forwarder.perform_pre_processing(binary)

        # Then
        assert actual.shape == expected_shape
        assert 0 <= actual.min() <= 255
        assert 0 <= actual.max() <= 255

    def test_perform_post_processing_should_transform_the_standard_output_from_the_model_into_the_expected_format(self):
        # Given
        model_forwarder = TFServingDetectionClassificationWrapper(
            base_url='',
            class_names_path=TEST_DATA_FOLDER_PATH / 'test_detection_foo_bar_baz_labels',
            image_shape=[1, 1]
        )
        json_outputs = {
            'detection_boxes': [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]],
            'detection_scores': [[0.8, 0.7, 0.6]],
            'detection_classes': [[1., 1., 2.]]
        }

        model = ModelInfos('id1', 'name1', 'detection', '1', 'camera_id1', [224, 224], class_names=['OK', 'KO'],
                           boxes_coordinates='detection_boxes', objectness_scores='detection_scores',
                           number_of_boxes='num_detections', detection_classes='detection_classes',
                           class_to_detect='foo', objectness_threshold=0.5)

        # crop_image expects the box coordinates to be (xmin, ymin, xmax, ymax)
        # Mobilenet returns the coordinates as (ymin, xmin, ymax, xmax)
        # Hence, the switch here

        expected = {
            'object_1': {
                'location': [2, 1, 4, 3],
                'score': 0.8,
                'label': 'bar'
            },
            'object_2': {
                'location': [6, 5, 8, 7],
                'score': 0.7,
                'label': 'bar'
            },
            'object_3': {
                'location': [10, 9, 12, 11],
                'score': 0.6,
                'label': 'baz'
            }
        }

        # When
        actual = model_forwarder.perform_post_processing(model, json_outputs)

        # Then
        assert actual == expected
