import json

from behave import given, then, use_step_matcher, when
from behave.runner import Context
from starlette.status import HTTP_200_OK

from tests.functional_tests.steps.common_steps import assert_metadata_almost_equal

use_step_matcher("re")


@given("the config '([a-zA-Z0-9-_]+)' is activated")
def config_is_activated(context: Context, config_name: str):
    with (context.test_directory / "config" / f"{config_name}.json").open("r") as f:
        config = json.load(f)

    context.execute_steps(
        """
            When the client activates configuration '{config_name}'
            Then the active configuration is
            \"\"\"
            {config}
            \"\"\"
        """.format(
            config_name=config_name, config=json.dumps(config)
        )
    )


@given("the following cameras are registered in the configuration")
def following_cameras_are_registered_in_the_configuration(context: Context):
    response = context.test_client.get("/api/v1/configs/active")
    assert response.status_code == HTTP_200_OK

    response_content = response.json()
    cameras = {}
    for row in context.table:
        current_camera_conf = response_content["camera_configs"][row["camera_id"]]
        cameras[row["camera_id"]] = current_camera_conf
        assert current_camera_conf["camera_type"] == row["camera_type"]
        assert current_camera_conf["position"] == row["position"]
        assert current_camera_conf["source_directory"] == row["source_directory"]
    context.cameras = cameras
    assert len(response_content["camera_configs"].keys()) == len(context.table.rows)


@when("the client triggers a visual inspection")
def client_triggers_visual_inspection(context: Context):
    response = context.test_client.post("/api/v1/trigger")
    assert response.status_code == HTTP_200_OK
    context.item_id = response.json()["item_id"]


@then("item metadata are like the following")
def item_metadata_like_following_are_captured(context: Context):
    response = context.test_client.get(f"/api/v1/items/{context.item_id}")
    assert response.status_code == HTTP_200_OK
    actual_item_metadata = response.json()
    expected_item_metadata = json.loads(context.text)
    assert_metadata_almost_equal(actual_item_metadata, expected_item_metadata)


@then("the item binaries are stored")
def check_item_binaries_are_stored(context: Context):
    response_1 = context.test_client.get(f"/api/v1/items/{context.item_id}/binaries")
    assert response_1.status_code == HTTP_200_OK

    response_1_content = response_1.json()
    for row in context.table:
        image_name = f'{row["binary_name"]}.{row["binary_extension"]}'
        assert image_name in response_1_content

        path_to_image = context.test_directory / f"data_storage/{context.item_id}" / image_name
        assert path_to_image.exists()
        with path_to_image.open("rb") as f:
            image_binary = f.read()

        response_2 = context.test_client.get(f'/api/v1/items/{context.item_id}/binaries/{row["binary_name"]}')
        assert response_2.status_code == HTTP_200_OK
        assert response_2.content == image_binary
    assert len(response_1_content) == len(context.table.rows)
