import re
from pathlib import Path
from typing import Dict, Union

import dateutil
from behave import given
from behave.runner import Context
from starlette.status import HTTP_200_OK


@given("the app is up and running")
def app_up_and_running(context: Context):
    response = context.test_client.get("/api/v1")
    assert response.status_code == HTTP_200_OK


def assert_metadata_almost_equal(
    actual_item_metadata: Dict[str, Union[Dict, str]],
    expected_item_metadata: Dict[str, Union[Dict, str]],
):
    for (
        expected_item_key,
        expected_item_value_or_pattern,
    ) in expected_item_metadata.items():
        if expected_item_key == "id":
            assert re.match(expected_item_value_or_pattern, actual_item_metadata[expected_item_key])
        elif expected_item_key == "creation_date":
            assert dateutil.parser.isoparse(actual_item_metadata[expected_item_key])
        elif expected_item_key == "binaries":
            assert_binaries_almost_equal(actual_item_metadata[expected_item_key])
        elif expected_item_key == "predictions":
            assert_predictions_almost_equal(actual_item_metadata[expected_item_key], expected_item_value_or_pattern)
        else:
            assert expected_item_value_or_pattern == actual_item_metadata[expected_item_key]


def assert_binaries_almost_equal(actual_binaries: Dict[str, Dict]):
    for camera_id, binary in actual_binaries.items():
        assert camera_id in actual_binaries
        assert dateutil.parser.isoparse(binary["creation_date"])
        assert Path(binary["storing_path"]).exists()


def assert_predictions_almost_equal(
    actual_predictions: Dict[str, Dict], expected_item_value_or_pattern: Dict[str, Dict]
):
    for camera_id, prediction in expected_item_value_or_pattern.items():
        assert camera_id in actual_predictions
        assert prediction["prediction_type"] == actual_predictions[camera_id]["prediction_type"]
        if prediction["prediction_type"] == "class":
            assert prediction["label"] == actual_predictions[camera_id]["label"]
            assert 0 < actual_predictions[camera_id]["probability"] < 1
        else:
            assert len(actual_predictions[camera_id]["detected_objects"]) > 0
            for key in ["location", "objectness", "label"]:
                assert key in actual_predictions[camera_id]["detected_objects"]["object_1"]
