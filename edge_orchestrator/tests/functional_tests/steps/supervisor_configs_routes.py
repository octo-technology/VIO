import json

from behave import then, use_step_matcher, when
from behave.runner import Context
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

use_step_matcher("re")


@when("the client requests the active configuration")
def client_requests_active_conf(context: Context):
    context.response = context.test_client.get("/api/v1/configs/active")
    assert context.response.status_code == HTTP_400_BAD_REQUEST


@when("the client requests all available configurations")
def client_requests_all_configurations(context: Context):
    context.response = context.test_client.get("/api/v1/configs")
    assert context.response.status_code == HTTP_200_OK


@when("the client activates configuration '([a-zA-Z0-9-_]+)'")
def client_set_active_configuration_as(context: Context, config_name: str):
    # TODO: update edge_interface to pass it as query param (not body!)
    context.response = context.test_client.post(f"/api/v1/configs/active/{config_name}")
    assert context.response.status_code == HTTP_200_OK


@then("the active configuration is")
def active_configuration_is(context: Context):
    config = json.loads(context.text)
    assert context.response.json() == config


@then("the client receives all available configurations")
def client_receives_all_available_configuration(context: Context):
    configs = {}
    for row in context.table:
        filepath = context.test_directory / row["config_filepath"]
        with filepath.open("r") as f:
            configs[filepath.stem] = json.load(f)
    for config_name, config in context.response.json().items():
        assert configs[config_name] == config
