import re
from typing import Dict, Union, Optional

from behave import given
from behave.runner import Context
from starlette.status import HTTP_200_OK
from time import strptime


@given("the app is up and running")
def app_up_and_running(context: Context):
    response = context.test_client.get("/api/v1")
    assert response.status_code == HTTP_200_OK


def assert_metadata_almost_equal(actual_item_metadata: Dict[str, Union[Dict, str]],
                                 expected_item_metadata: Dict[str, Union[Dict, str]]):
    for expected_item_key, expected_item_value_or_pattern in expected_item_metadata.items():
        if expected_item_key == '_id':
            assert re.match(expected_item_value_or_pattern, actual_item_metadata[expected_item_key])
        elif expected_item_key == 'received_time':
            assert strptime(actual_item_metadata[expected_item_key], expected_item_value_or_pattern)
        elif expected_item_key == 'inferences':
            assert_classification_inference_almost_equal(actual_item_metadata[expected_item_key],
                                                         expected_item_value_or_pattern)
        elif expected_item_key == 'decision':
            assert_decision_is_valid(actual_item_metadata[expected_item_key], expected_item_value_or_pattern)
        elif expected_item_key == 'state':
            assert_state_is_valid(actual_item_metadata[expected_item_key], expected_item_value_or_pattern)
        else:
            assert expected_item_value_or_pattern == actual_item_metadata[expected_item_key]


def assert_classification_inference_almost_equal(actual_inference: Dict[str, Dict],
                                                 expected_item_value_or_pattern: Dict[str, Dict]):
    for camera_id, cam_inferences in expected_item_value_or_pattern.items():
        assert camera_id in actual_inference
        for model_id, inference in cam_inferences.items():
            assert model_id in actual_inference[camera_id]
            assert re.match(inference['full_image']['label'],
                            actual_inference[camera_id][model_id]['full_image']['label'])
            assert re.match(inference['full_image']['probability'],
                            str(actual_inference[camera_id][model_id]['full_image'][
                                    'probability']))


def assert_state_is_valid(actual_state: str, expected_state: Optional[str] = None):
    from supervisor.domain.use_cases.supervisor import SupervisorState
    if expected_state:
        assert re.match(expected_state, actual_state)
    else:
        assert actual_state in [state.value for state in SupervisorState]


def assert_decision_is_valid(actual_decision: str, expected_decision: Optional[str] = None):
    if expected_decision:
        assert re.match(expected_decision, actual_decision)
    else:
        from supervisor.domain.models.decision import Decision
        assert actual_decision in [decision.value for decision in Decision]
