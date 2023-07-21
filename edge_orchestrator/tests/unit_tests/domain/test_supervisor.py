import logging
import random
from unittest.mock import patch

import numpy as np
import pytest

from edge_orchestrator.domain.models.edge_station import EdgeStation
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.domain.use_cases.supervisor import crop_image, Supervisor
from edge_orchestrator.infrastructure.binary_storage.in_memory_binary_storage import (
    InMemoryBinaryStorage,
)
from edge_orchestrator.infrastructure.metadata_storage.in_memory_metadata_storage import (
    InMemoryMetadataStorage,
)
from edge_orchestrator.infrastructure.model_forward.fake_model_forward import (
    FakeModelForward,
)
from edge_orchestrator.infrastructure.station_config.json_station_config import (
    JsonStationConfig,
)
from edge_orchestrator.infrastructure.telemetry_sink.fake_telemetry_sink import (
    FakeTelemetrySink,
)
from edge_orchestrator.infrastructure.telemetry_sink.postgres_telemetry_sink import (
    PostgresTelemetrySink,
)
from tests.conftest import (
    TEST_DATA_FOLDER_PATH,
    TEST_STATION_CONFIGS_FOLDER_PATH,
)


@pytest.mark.asyncio
class TestSupervisor:
    async def test_2_models_in_parallel(self, supervisor):
        random.seed(42)
        np.random.seed(42)

        models_graph = {
            "model_1": {"name": "inception", "depends_on": []},
            "model_2": {"name": "inception", "depends_on": []},
        }

        model_pipeline = [
            ModelInfos.from_model_graph_node(
                "camera_id", model_id, model, TEST_DATA_FOLDER_PATH
            )
            for model_id, model in models_graph.items()
        ]
        binary_data = b"fhfh"

        supervisor.model_forward = FakeModelForward()
        inference_output = await supervisor.get_inference(
            {}, model_pipeline, binary_data, image_name="full_image"
        )

        inference_output_expected = {
            "model_1": {
                "full_image": {"label": "OK", "probability": 0.3745401188473625}
            },
            "model_2": {
                "full_image": {"label": "OK", "probability": 0.9507143064099162}
            },
        }

        assert inference_output == inference_output_expected

    async def test_2_models_in_serie(self, supervisor):
        random.seed(42)
        np.random.seed(42)

        models_graph = {
            "model_1": {"name": "inception", "depends_on": ["model_2"]},
            "model_2": {"name": "mobilenet_v1_640x640", "depends_on": []},
        }

        model_pipeline = [
            ModelInfos.from_model_graph_node(
                "camera_id", model_id, model, TEST_DATA_FOLDER_PATH
            )
            for model_id, model in models_graph.items()
        ]
        binary_data = (
            (TEST_DATA_FOLDER_PATH / "fake_item" / "image1.jpg").open("rb").read()
        )

        supervisor.model_forward = FakeModelForward()
        inference_output = await supervisor.get_inference(
            {}, model_pipeline, binary_data, image_name="full_image"
        )

        inference_output_expected = {
            "model_1": {
                "full_image_object_1": {
                    "label": "OK",
                    "probability": 0.7319939418114051,
                },
                "full_image_object_2": {
                    "label": "OK",
                    "probability": 0.5986584841970366,
                },
            },
            "model_2": {
                "full_image_object_1": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.3745401188473625,
                },
                "full_image_object_2": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.9507143064099162,
                },
            },
        }

        assert inference_output == inference_output_expected

    @patch.object(JsonStationConfig, "get_model_pipeline_for_camera")
    @pytest.mark.parametrize(
        "camera_id", ["camera_id1", "camera_id2", "camera_id3", "camera_id4"]
    )
    async def test_get_prediction_for_camera_should_return_2_predicted_objects_by_one_object_detection_model(
        self, model_config_mocked, camera_id, my_item_1
    ):
        # Given
        np.random.seed(42)
        supervisor = Supervisor(model_forward=FakeModelForward())
        model_infos = [
            ModelInfos(
                id="model1",
                depends_on=[],
                name="mobilenet_v1_640x640",
                category="object_detection",
                version="1",
                camera_id=camera_id,
            )
        ]
        model_config_mocked.return_value = model_infos

        expected = {
            "model1": {
                "full_image_object_1": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.3745401188473625,
                },
                "full_image_object_2": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.9507143064099162,
                },
            }
        }

        # When
        actual = await supervisor.get_prediction_for_camera(
            camera_id, my_item_1, image_name="full_image"
        )

        # Then
        assert actual == expected

    @patch.object(JsonStationConfig, "get_model_pipeline_for_camera")
    @pytest.mark.parametrize(
        "camera_id", ["camera_id1", "camera_id2", "camera_id3", "camera_id4"]
    )
    async def test_get_prediction_for_camera_should_return_1_predicted_object_by_one_classification_model(
        self, model_config_mocked, camera_id, my_item_1
    ):
        # Given
        np.random.seed(42)
        random.seed(42)
        supervisor = Supervisor(model_forward=FakeModelForward())
        models_version = [
            ModelInfos(
                id="model1",
                depends_on=[],
                name="inspection",
                category="classification",
                version="1",
                camera_id=camera_id,
            )
        ]
        model_config_mocked.return_value = models_version

        expected = {
            "model1": {"full_image": {"label": "OK", "probability": 0.3745401188473625}}
        }

        # When
        actual = await supervisor.get_prediction_for_camera(
            camera_id, my_item_1, image_name="full_image"
        )

        # Then
        assert actual == expected

    @patch.object(JsonStationConfig, "get_model_pipeline_for_camera")
    @pytest.mark.parametrize(
        "camera_id", ["camera_id1", "camera_id2", "camera_id3", "camera_id4"]
    )
    async def test_get_prediction_for_camera_returns_2_objects_with_label_for_object_detection_followed_by_classif(
        # noqa
        self,
        model_config_mocked,
        camera_id,
        my_item_1,
    ):
        # Given
        np.random.seed(42)
        random.seed(42)
        supervisor = Supervisor(model_forward=FakeModelForward())
        models_version = [
            ModelInfos(
                id="model1",
                depends_on=[],
                name="mobilenet_v1_640x640",
                category="object_detection",
                version="1",
                camera_id=camera_id,
            ),
            ModelInfos(
                id="model2",
                depends_on=["model1"],
                name="inception",
                category="classification",
                version="1",
                camera_id=camera_id,
            ),
        ]

        model_config_mocked.return_value = models_version

        expected = {
            "model1": {
                "full_image_object_1": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.3745401188473625,
                },
                "full_image_object_2": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.9507143064099162,
                },
            },
            "model2": {
                "full_image_object_1": {
                    "label": "OK",
                    "probability": 0.7319939418114051,
                },
                "full_image_object_2": {
                    "label": "OK",
                    "probability": 0.5986584841970366,
                },
            },
        }

        # When
        actual = await supervisor.get_prediction_for_camera(
            camera_id, my_item_1, image_name="full_image"
        )

        # Then
        assert actual == expected

    @patch.object(JsonStationConfig, "get_model_pipeline_for_camera")
    @pytest.mark.parametrize(
        "camera_id", ["camera_id1", "camera_id2", "camera_id3", "camera_id4"]
    )
    async def test_get_prediction_for_camera_returns_2_objects_with_label_for_object_detection_with_classif_model(
        # noqa
        self,
        model_config_mocked,
        camera_id,
        my_item_1,
    ):
        # Given
        np.random.seed(42)
        random.seed(42)
        supervisor = Supervisor(model_forward=FakeModelForward())
        models_version = [
            ModelInfos(
                id="model1",
                depends_on=[],
                name="mobilenet_v1_640x640_detect_classif",
                category="object_detection_with_classification",
                version="1",
                camera_id=camera_id,
            ),
        ]
        expected = {
            "model1": {
                "full_image_object_1": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.3745401188473625,
                    "label": "OK",
                    "probability": 0.9507143064099162,
                },
                "full_image_object_2": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.7319939418114051,
                    "label": "OK",
                    "probability": 0.5986584841970366,
                },
            }
        }

        model_config_mocked.return_value = models_version

        # When
        actual = await supervisor.get_prediction_for_camera(
            camera_id, my_item_1, image_name="full_image"
        )

        # Then
        assert actual == expected

    @patch.object(JsonStationConfig, "get_model_pipeline_for_camera")
    @pytest.mark.parametrize(
        "camera_id", ["camera_id1", "camera_id2", "camera_id3", "camera_id4"]
    )
    async def test_get_prediction_for_camera_should_return_1_output_by_model_and_among_them_1_is_classification(
        # noqa
        self,
        model_config_mocked,
        camera_id,
        my_item_1,
    ):
        # Given
        np.random.seed(42)
        random.seed(42)
        supervisor = Supervisor(model_forward=FakeModelForward())
        models_version = [
            ModelInfos(
                id="model1",
                depends_on=[],
                name="mobilenet_v1_640x640",
                category="object_detection",
                version="1",
                camera_id=camera_id,
            ),
            ModelInfos(
                id="model2",
                depends_on=["model1"],
                name="mobilenet_v1_640x640",
                category="object_detection",
                version="1",
                camera_id=camera_id,
            ),
            ModelInfos(
                id="model3",
                depends_on=["model2"],
                name="inception",
                category="classification",
                version="1",
                camera_id=camera_id,
            ),
        ]

        model_config_mocked.return_value = models_version

        expected = {
            "model1": {
                "full_image_object_1": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.3745401188473625,
                },
                "full_image_object_2": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.9507143064099162,
                },
            },
            "model2": {
                "full_image_object_1_object_1": {
                    "location": [8, 224, 248, 268],
                    "objectness": 0.7319939418114051,
                },
                "full_image_object_1_object_2": {
                    "location": [8, 224, 248, 268],
                    "objectness": 0.5986584841970366,
                },
                "full_image_object_2_object_1": {
                    "location": [8, 224, 248, 268],
                    "objectness": 0.15601864044243652,
                },
                "full_image_object_2_object_2": {
                    "location": [8, 224, 248, 268],
                    "objectness": 0.15599452033620265,
                },
            },
            "model3": {
                "full_image_object_1_object_1": {
                    "label": "OK",
                    "probability": 0.05808361216819946,
                },
                "full_image_object_1_object_2": {
                    "label": "OK",
                    "probability": 0.8661761457749352,
                },
                "full_image_object_2_object_1": {
                    "label": "KO",
                    "probability": 0.6011150117432088,
                },
                "full_image_object_2_object_2": {
                    "label": "OK",
                    "probability": 0.7080725777960455,
                },
            },
        }

        # When
        actual = await supervisor.get_prediction_for_camera(
            camera_id, my_item_1, image_name="full_image"
        )

        # Then
        assert actual == expected

    @patch.object(JsonStationConfig, "get_model_pipeline_for_camera")
    @pytest.mark.parametrize(
        "camera_id", ["camera_id1", "camera_id2", "camera_id3", "camera_id4"]
    )
    async def test_get_prediction_for_camera_should_return_1_output_by_model_and_among_them_2_are_classification(
        # noqa
        self,
        model_config_mocked,
        camera_id,
        my_item_1,
    ):
        # Given
        np.random.seed(42)
        random.seed(42)
        supervisor = Supervisor(model_forward=FakeModelForward())
        models_version = [
            ModelInfos(
                id="model1",
                depends_on=[],
                name="mobilenet_v1_640x640",
                category="object_detection",
                version="1",
                camera_id=camera_id,
            ),
            ModelInfos(
                id="model2",
                depends_on=["model1"],
                name="mobilenet_v1_640x640",
                category="object_detection",
                version="1",
                camera_id=camera_id,
            ),
            ModelInfos(
                id="model3",
                depends_on=["model2"],
                name="inception",
                category="classification",
                version="1",
                camera_id=camera_id,
            ),
            ModelInfos(
                id="model4",
                depends_on=[],
                name="inception",
                category="classification",
                version="1",
                camera_id=camera_id,
            ),
        ]

        model_config_mocked.return_value = models_version

        expected = {
            "model1": {
                "full_image_object_1": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.3745401188473625,
                },
                "full_image_object_2": {
                    "location": [4, 112, 244, 156],
                    "objectness": 0.9507143064099162,
                },
            },
            "model2": {
                "full_image_object_1_object_1": {
                    "location": [8, 224, 248, 268],
                    "objectness": 0.7319939418114051,
                },
                "full_image_object_1_object_2": {
                    "location": [8, 224, 248, 268],
                    "objectness": 0.5986584841970366,
                },
                "full_image_object_2_object_1": {
                    "location": [8, 224, 248, 268],
                    "objectness": 0.15601864044243652,
                },
                "full_image_object_2_object_2": {
                    "location": [8, 224, 248, 268],
                    "objectness": 0.15599452033620265,
                },
            },
            "model3": {
                "full_image_object_1_object_1": {
                    "label": "OK",
                    "probability": 0.05808361216819946,
                },
                "full_image_object_1_object_2": {
                    "label": "OK",
                    "probability": 0.8661761457749352,
                },
                "full_image_object_2_object_1": {
                    "label": "KO",
                    "probability": 0.6011150117432088,
                },
                "full_image_object_2_object_2": {
                    "label": "OK",
                    "probability": 0.7080725777960455,
                },
            },
            "model4": {
                "full_image": {"label": "OK", "probability": 0.020584494295802447}
            },
        }

        # When
        actual = await supervisor.get_prediction_for_camera(
            camera_id, my_item_1, image_name="full_image"
        )

        # Then
        assert actual == expected

    def test_apply_crop_function_with_correct_box_should_resize_the_picture(self):
        # Given
        original_picture = (
            (TEST_DATA_FOLDER_PATH / "fake_item" / "image3.jpg").open("rb").read()
        )
        expected_cropped_picture = (
            (TEST_DATA_FOLDER_PATH / "fake_item" / "image3_crop.jpg").open("rb").read()
        )

        # xmin, ymin, xmax, ymax
        box = [218, 41, 553, 379]

        # When
        actual = crop_image(original_picture, box)

        # Then
        assert actual == expected_cropped_picture

    def test_apply_crop_function_with_incorrect_box_should_log_an_error_and_return_the_same_picture(
        self, caplog
    ):
        # Given
        original_picture = (
            (TEST_DATA_FOLDER_PATH / "fake_item" / "image3.jpg").open("rb").read()
        )

        # xmin, ymin, xmax, ymax
        box = [554, 41, 553, 379]

        # When
        actual = crop_image(original_picture, box)

        # Then
        assert actual == original_picture
        assert (
            caplog.records[0].msg
            == "Informations for cropping are incorrect, the initial picture is used"
        )
        assert caplog.records[1].msg == "xmin (=554) is greater than xmax (=553)"

    @patch.object(PostgresTelemetrySink, "send")
    async def test_set_decision_should_send_final_decision_to_telemetry_sink(
        self, mock_send
    ):
        # Given
        item = Item(serial_number="", category="", cameras_metadata={}, binaries={})
        item.id = "item_id"
        station_config = JsonStationConfig(
            TEST_STATION_CONFIGS_FOLDER_PATH, TEST_DATA_FOLDER_PATH
        )
        station_config.set_station_config("station_config_TEST")
        supervisor = Supervisor(
            binary_storage=InMemoryBinaryStorage(),
            edge_station=EdgeStation(station_config),
            metadata_storage=InMemoryMetadataStorage(),
            model_forward=FakeModelForward(),
            station_config=station_config,
            telemetry_sink=FakeTelemetrySink(),
        )

        # When
        await supervisor.inspect(item)

        # Then
        msg_dict = {
            "item_id": "item_id",
            "config": "station_config_TEST",
            "decision": "OK",
        }
        mock_send.assert_called_once_with(msg_dict)

    async def test_inspect_should_log_information_about_item_processing(
        self, caplog, my_fake_item
    ):
        # Given
        expected_messages = [
            "Activated the configuration station_config_TEST",
            "Starting Capture",
            "Entering try Capture",
            "End of Capture",
            "Starting Save Binaries",
            "Entering try Save Binaries",
            "End of Save Binaries",
            "Starting Inference",
            "Entering try Inference",
            "Getting inference for model model_id4",
            "End of Inference",
            "Starting Decision",
            "Entering try Decision",
            "End of Decision",
        ]
        station_config = JsonStationConfig(
            TEST_STATION_CONFIGS_FOLDER_PATH, TEST_DATA_FOLDER_PATH
        )
        station_config.set_station_config("station_config_TEST")
        supervisor = Supervisor(
            binary_storage=InMemoryBinaryStorage(),
            edge_station=EdgeStation(station_config),
            metadata_storage=InMemoryMetadataStorage(),
            model_forward=FakeModelForward(),
            station_config=station_config,
            telemetry_sink=FakeTelemetrySink(),
        )

        # When
        with caplog.at_level(logging.INFO, logger="edge_orchestrator"):
            await supervisor.inspect(my_fake_item)

        # Then
        actual_messages = [
            logger_msg
            for logger_name, logger_level, logger_msg in caplog.record_tuples
            if logger_name == "edge_orchestrator"
        ]
        assert expected_messages == actual_messages
