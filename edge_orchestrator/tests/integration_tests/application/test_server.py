import json
import datetime as dt

from freezegun import freeze_time
from fastapi.testclient import TestClient

from tests.conftest import TEST_DATA_FOLDER_PATH
from edge_orchestrator.application.server import server
from edge_orchestrator.api_config import get_metadata_storage

class TestServer:
    def test_upload_route__should_return_expected_logs_when_received_paylod_with_binary_image(
            self,
            caplog):
        # Given
        client = TestClient(server())
        test_file = 'camera_id1.jpg'
        test_file_path = TEST_DATA_FOLDER_PATH / 'item_2' / test_file
        expected_logs = ["Starting Save Binaries",
                         "Entering try Save Binaries",
                         "End of Save Binaries"]

        # When
        with open(test_file_path, "rb") as f:
            actual_response = client.post("/api/v1/upload", files={"image": ("filename", f, "image/jpeg")})

        actual_logs = []
        for record in caplog.records:
            if record.funcName == "upload":
                actual_logs.append(record.msg)
        # Then
        assert actual_response.status_code == 200
        assert actual_logs == expected_logs

    @freeze_time(lambda: dt.datetime(year=2021, month=5, day=19, hour=15, minute=0, second=0))
    def test_get_item_metadata__should_return_expected_paylod_when_received_specific_item_id(
            self,
            mock_get_metadata_storage,
            my_item_0,
            caplog):
        # Given
        metadata_storage = get_metadata_storage()
        metadata_storage.save_item_metadata(my_item_0)
        client = TestClient(server())
        test_item_id = my_item_0.id
        keys_expected = ['id', 'serial_number', 'category', 'station_config', 'cameras', 'received_time', 'inferences',
                         'decision', 'state', 'error']

        # When
        actual_response = client.get(f'/items/{test_item_id}')

        # Then
        assert actual_response.status_code == 200
        json_response = json.loads(actual_response.text)
        assert len(json_response) == 10
        assert json_response["id"] == test_item_id
        assert list(json_response.keys()) == keys_expected
