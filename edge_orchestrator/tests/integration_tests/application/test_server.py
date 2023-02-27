from fastapi.testclient import TestClient
from tests.conftest import TEST_DATA_FOLDER_PATH

from edge_orchestrator.application.server import server


class TestServer:
    def test_upload_route__should_return_expected_logs_when_received_paylod_with_binary_image(
            self,
            caplog):
        # Given
        client = TestClient(server())
        test_file = 'camera_id1.jpg'
        test_file_path = TEST_DATA_FOLDER_PATH / 'item_2' / test_file
        expected_logs = ["Starting Capture",
                         "Entering try Capture",
                         "Error during Capture: 'NoneType' object is not subscriptable",
                         "End of Capture",
                         "Starting Save Binaries",
                         "Entering try Save Binaries",
                         "End of Save Binaries",
                         "Starting Inference",
                         "Entering try Inference",
                         "Error during Inference: 'NoneType' object is not subscriptable",
                         "End of Inference",
                         "Starting Decision",
                         "Entering try Decision",
                         "Error during Decision: 'NoneType' object is not subscriptable",
                         "End of Decision"]

        # When
        with open(test_file_path, "rb") as f:
            actual_response = client.post("/api/v1/upload", files={"image": ("filename", f, "image/jpeg")})

        actual_logs = []
        for record in caplog.records:
            if record.funcName == "inspect":
                actual_logs.append(record.msg)
        # Then
        assert actual_response.status_code == 200
        assert actual_logs == expected_logs
