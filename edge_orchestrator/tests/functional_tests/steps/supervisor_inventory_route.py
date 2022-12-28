import json

from behave import when, then, use_step_matcher
from behave.runner import Context
from starlette.status import HTTP_200_OK

use_step_matcher("re")


@when("the client requests the inventory")
def client_requests_inventory(context: Context):
    context.response = context.test_client.get("/api/v1/inventory")
    assert context.response.status_code == HTTP_200_OK


@then("the client receives the following inventory")
def client_receives_the_following_inventory(context: Context):
    inventory = json.loads(context.text)
    assert context.response.json() == inventory
