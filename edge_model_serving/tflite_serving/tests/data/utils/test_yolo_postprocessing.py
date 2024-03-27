import numpy as np
from tflite_serving.utils.yolo_postprocessing import (
    yolo_extract_boxes_information,
    nms,
    compute_severities,
)


class TestYoloPostprocessing:
    def test_yolo_extract_boxes_information(self):
        # Given
        model_outputs = np.array(
            [
                [100, 120, 50, 30, 0.8, 0.1, 0.001],
                [300, 220, 30, 26, 0.01, 0.99, 0.001],
                [110, 125, 40, 20, 0.9, 0.01, 0.01],
            ]
        )
        expected_boxes = [
            [75, 105, 125, 135],
            [285, 207, 315, 233],
            [90, 115, 130, 135],
        ]
        expected_scores = [0.8, 0.99, 0.9]
        expected_classes = [0, 1, 0]

        # When
        boxes, scores, classes = yolo_extract_boxes_information(model_outputs)

        # Then
        assert boxes == expected_boxes
        assert scores == expected_scores
        assert classes == expected_classes

    def test_nms(self):
        # Given
        boxes = [
            [75, 105, 125, 135],
            [285, 207, 315, 233],
            [90, 115, 130, 135],
            [90, 115, 130, 135],
            [120, 130, 200, 155],
        ]
        scores = [0.8, 0.99, 0.9, 0.34, 0.75]
        classes = [0, 1, 0, 2, 0]

        # When
        expected_boxes = [
            [285, 207, 315, 233],
            [90, 115, 130, 135],
            [120, 130, 200, 155],
        ]
        expected_scores = [0.99, 0.9, 0.75]
        expected_classes = [1, 0, 0]

        nms_boxes, nms_scores, nms_classes = nms(
            boxes, scores, classes, score_threshold=0.4, iou_threshold=0.45
        )

        # Then
        assert nms_boxes == expected_boxes
        assert nms_scores == expected_scores
        assert nms_classes == expected_classes

    def test_compute_severities(self):
        # Given
        image = np.array(
            [
                [
                    [1, 1, 1],
                    [1, 1, 1],
                    [0.8, 0.8, 0.8],
                    [1, 1, 1],
                    [1, 1, 1]],
                [
                    [0.8, 0.8, 0.8],
                    [0.8, 0.8, 0.8],
                    [0.6, 0.6, 0.6],
                    [0.8, 0.8, 0.8],
                    [0.8, 0.8, 0.8],
                ],
                [
                    [0.6, 0.6, 0.6],
                    [0.2, 0.2, 0.2],
                    [0.0, 0.0, 0.0],
                    [0.2, 0.2, 0.2],
                    [0.6, 0.6, 0.6],
                ],
                [
                    [0.6, 0.6, 0.6],
                    [0.2, 0.2, 0.2],
                    [0.0, 0.0, 0.0],
                    [0.2, 0.2, 0.2],
                    [0.6, 0.6, 0.6],
                ],
                [
                    [0.8, 0.8, 0.8],
                    [0.8, 0.8, 0.8],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.8, 0.8, 0.8],
                ],
            ]
        )
        boxes = [[0.23, 0.23, 1, 1], [0.1, 0.05, 0.4, 0.2]]
        expected_severities = [0.8, 0.1]

        # When
        severities = compute_severities(image, boxes)

        # Then
        assert severities == expected_severities
