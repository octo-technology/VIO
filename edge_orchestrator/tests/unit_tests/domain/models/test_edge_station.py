import datetime as dt
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from edge_orchestrator.api_config import get_station_config
from edge_orchestrator.domain.models.edge_station import EdgeStation
from edge_orchestrator.domain.ports.station_config import StationConfig
from edge_orchestrator.infrastructure.camera.fake_camera import FakeCamera


class TestEdgeStation:
    def test_register_cameras_raises_exception_when_no_active_configuration_is_set(
        self,
    ):
        # Given
        station_config: StationConfig = get_station_config()

        edge_station = EdgeStation(station_config)

        # Then
        with pytest.raises(TypeError) as error:
            edge_station.register_cameras(station_config)
        assert str(error.value) == "'NoneType' object is not subscriptable"

    def test_capture_should_raise_exception_when_cameras_are_not_registered(self):
        # Given
        station_config: StationConfig = get_station_config()
        station_config.set_station_config("station_config_TEST")

        edge_station = EdgeStation(station_config)

        # Then
        with pytest.raises(AttributeError) as error:
            edge_station.capture()
        assert str(error.value) == "'EdgeStation' object has no attribute 'cameras'"

    @freeze_time(lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0))
    @patch.object(FakeCamera, "capture")
    @patch("edge_orchestrator.domain.models.item.generate_id")
    def test_capture_should_instantiate_item_with_1_binary(
        self, generate_id_mocked, capture_mocked, my_fake_item_2, my_fake_binaries_2
    ):
        # Given
        # random.seed(123)

        expected_id = "my_fake_item_id"
        generate_id_mocked.return_value = expected_id
        capture_mocked.return_value = my_fake_binaries_2

        my_fake_item_2.id = expected_id

        station_config: StationConfig = get_station_config()
        station_config.set_station_config("station_config_TEST")

        edge_station = EdgeStation(station_config)

        # When
        edge_station.register_cameras(station_config)
        cameras_metadata, binaries = edge_station.capture()

        # Then
        assert cameras_metadata == my_fake_item_2.cameras_metadata
        capture_mocked.assert_called_once()
