import datetime as dt
import os

import pytest
from freezegun import freeze_time

from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.infrastructure.station_config.json_station_config import (
    JsonStationConfig,
)
from tests.conftest import (
    TEST_DATA_FOLDER_PATH,
    TEST_STATION_CONFIGS_FOLDER_PATH,
)


@freeze_time(
    lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0)
)
class TestJsonStationConfig:
    def test_get_models_for_camera_should_return_one_model_infos_when_camera_config_has_one_model(
        self,
    ):
        # Given
        json_station_config = JsonStationConfig(
            TEST_STATION_CONFIGS_FOLDER_PATH, TEST_DATA_FOLDER_PATH
        )
        camera_id = "camera_id3"

        # When
        with pytest.raises(TypeError) as error:
            json_station_config.get_model_pipeline_for_camera(camera_id)

        assert str(error.value) == "'NoneType' object is not subscriptable"

    def test_get_models_for_camera_should_return_two_model_infos_when_camera_config_has_two_models(
        self,
    ):
        # Given
        json_station_config = JsonStationConfig(
            TEST_STATION_CONFIGS_FOLDER_PATH, TEST_DATA_FOLDER_PATH
        )
        json_station_config.set_station_config("station_config_TEST2")
        camera_id = "camera_id3"

        expected = [
            ModelInfos(
                id="model_1",
                depends_on=[],
                name="mobilenet_v1_640x640",
                category="object_detection",
                class_names=None,
                class_names_path=os.path.join(
                    TEST_DATA_FOLDER_PATH, "test_detection_labels"
                ),
                version="1",
                camera_id="camera_id3",
                boxes_coordinates="detection_boxes",
                objectness_scores="detection_scores",
                number_of_boxes="num_detections",
                class_to_detect="foo",
                detection_classes="detection_classes",
                objectness_threshold=0.5,
            ),
            ModelInfos(
                id="model_2",
                depends_on=["model_1"],
                name="inception",
                category="classification",
                class_names=["OK", "KO"],
                version="1",
                camera_id="camera_id3",
                image_resolution=[224, 224],
            ),
        ]

        # When
        actual = json_station_config.get_model_pipeline_for_camera(camera_id)

        # Then
        assert actual == expected
