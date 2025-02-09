import json

from fastapi.testclient import TestClient

from edge_orchestrator.api_config import get_metadata_storage
from edge_orchestrator.application.server import server
from tests.conftest import EDGE_NAME, TEST_DATA_FOLDER_PATH


class TestServer:
    def test_upload_route__should_return_expected_logs_when_received_paylod_with_binary_image(self, caplog):
        # Given
        client = TestClient(server())
        test_file = "camera_id1.jpg"
        test_file_path = TEST_DATA_FOLDER_PATH / EDGE_NAME / "test_config" / "item_2" / test_file
        expected_logs = [
            "Starting Save Binaries",
            "Entering try Save Binaries",
            "End of Save Binaries",
        ]
        client.post(
            "/api/v1/configs/active",
            json={"config_name": "marker_classification_with_2_fake_cameras"},
        )

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

    def test_get_item_metadata__should_return_expected_paylod_when_received_specific_item_id(self, my_item_0, caplog):
        # Given
        metadata_storage = get_metadata_storage()
        metadata_storage.save_item_metadata(my_item_0)
        client = TestClient(server())
        test_item_id = my_item_0.id
        keys_expected = [
            "serial_number",
            "category",
            "station_config",
            "cameras",
            "received_time",
            "dimensions",
            "inferences",
            "decision",
            "state",
            "error",
            "id",
        ]

        # When
        actual_response = client.get(f"/api/v1/items/{test_item_id}")

        # Then
        assert actual_response.status_code == 200
        json_response = json.loads(actual_response.text)
        assert len(json_response) == 11
        assert list(json_response.keys()) == keys_expected
