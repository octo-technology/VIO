import json

from behave import given, then, use_step_matcher, when
from behave.runner import Context

from tests.functional_tests.steps.common_steps import assert_metadata_almost_equal

use_step_matcher("re")


@given("item '([a-zA-Z0-9-_]+)' is stored")
def client_trigger_item_capture_and_storage(context: Context, item_id: str):
    response = context.test_client.post("/api/v1/trigger")
    assert response.status_code == 200
    context.item_id = response.json()["item_id"]


@when("the client requests the items metadata list")
def client_get_items(context: Context):
    context.response = context.test_client.get("/api/v1/items")
    assert context.response.status_code == 200


@when("the item '([a-zA-Z0-9-_]+)' metadata is requested")
def client_get_item_metadata(context: Context, item_id: str):
    response = context.test_client.get(f"/api/v1/items/{context.item_id}")
    assert response.status_code == 200
    context.json_response = response.json()


@when("one item '([a-zA-Z0-9-_]+)' binary from camera '([a-zA-Z0-9-_]+)' is requested")
def client_get_item_binary(context: Context, item_id: str, camera_id: str):
    response = context.test_client.get(f"/api/v1/items/{context.item_id}/binaries/{camera_id}")
    assert response.status_code == 200
    context.binary_response = response.content


@then("the client receives the items metadata list")
def check_response(context: Context):
    assert isinstance(context.response.json(), list)


@then("the item '([a-zA-Z0-9-_]+)' metadata is read")
def check_item_metadata_is_read(context: Context, item_id: str):
    response = context.test_client.get(f"/api/v1/items/{context.item_id}")
    assert response.status_code == 200
    actual_item_metadata = response.json()
    expected_item_metadata = json.loads(context.text)
    assert_metadata_almost_equal(actual_item_metadata, expected_item_metadata)


@then("one item '([a-zA-Z0-9-_]+)' binary from camera '([a-zA-Z0-9-_]+)' is read")
def check_item_binary_is_red(context: Context, item_id: str, camera_id: str):
    assert isinstance(context.binary_response, bytes)
