import json
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
from behave import given, when, then, use_step_matcher
from behave.runner import Context
from starlette.status import HTTP_200_OK

from edge_orchestrator.domain.models.decision import Decision
from tests.functional_tests.steps.common_steps import assert_metadata_almost_equal, assert_decision_is_valid, \
    assert_state_is_valid

use_step_matcher('re')


@given("the config '([a-zA-Z0-9-_]+)' is activated")
def config_is_activated(context: Context, config_name: str):
    with (context.test_directory / 'config' / 'station_configs' / f'{config_name}.json').open('r') as f:
        config = json.load(f)

    context.execute_steps(u'''
            When the client activates configuration '{station_config_TEST}'
            Then the active configuration is
            \"\"\"
            {config}
            \"\"\"
        '''.format(station_config_TEST=config_name, config=json.dumps(config)))


@given('the following cameras are registered in the configuration')
def following_cameras_are_registered_in_the_configuration(context: Context):
    response = context.test_client.get('/api/v1/configs/active')
    assert response.status_code == HTTP_200_OK

    response_content = response.json()
    cameras = {}
    for row in context.table:
        current_camera_conf = response_content['cameras'][row['camera_id']]
        cameras[row['camera_id']] = current_camera_conf
        assert current_camera_conf['type'] == row['camera_type']
        assert current_camera_conf['input_images_folder'] == row['input_images_folder']
    context.cameras = cameras
    assert len(response_content['cameras'].keys()) == len(context.table.rows)


@when('the client triggers a visual inspection')
def client_triggers_visual_inspection(context: Context):
    response = context.test_client.put('/api/v1/trigger')
    assert response.status_code == HTTP_200_OK

    context.item_id = response.json()['item_id']


@then('item metadata like the following are captured')
def item_metadata_like_following_are_captured(context: Context):
    response = context.test_client.get(f'/api/v1/items/{context.item_id}')
    assert response.status_code == HTTP_200_OK

    actual_item_metadata = response.json()
    expected_item_metadata = json.loads(context.text)
    assert_metadata_almost_equal(actual_item_metadata, expected_item_metadata)


@then('the item binaries are stored')
def check_item_binaries_are_stored(context: Context):
    response_1 = context.test_client.get(f'/api/v1/items/{context.item_id}/binaries')
    assert response_1.status_code == HTTP_200_OK

    response_1_content = response_1.json()
    for row in context.table:
        assert f'{row["binary_name"]}.{row["binary_extension"]}' in response_1_content

        path_to_tests_images = context.test_directory / 'data' / context.cameras[row['binary_name']][
            'input_images_folder']
        tests_images = [filepath.open('rb').read() for filepath in path_to_tests_images.iterdir()
                        if filepath.suffix == '.jpg']

        response_2 = context.test_client.get(f'/api/v1/items/{context.item_id}/binaries/{row["binary_name"]}')
        assert response_2.status_code == HTTP_200_OK
        assert response_2.content in tests_images
    assert len(response_1_content) == len(context.table.rows)


@then('the item inference is computed')
def check_inference_is_computed(context: Context):
    response = context.test_client.get(f'/api/v1/items/{context.item_id}')
    assert response.status_code == HTTP_200_OK
    expected_item_metadata = json.loads(context.text)
    context.execute_steps(u'''
            Then item metadata like the following are captured
            \"\"\"
            {item_metadata}
            \"\"\"
        '''.format(item_metadata=json.dumps(expected_item_metadata)))


@then('the item decision is made')
def check_business_value_is_made(context: Context):
    response = context.test_client.get(f'/api/v1/items/{context.item_id}')
    assert response.status_code == HTTP_200_OK
    assert_decision_is_valid(response.json()['decision'])


@then('the item state is set to done')
def check_state_is_done(context: Context):
    response = context.test_client.get(f'/api/v1/items/{context.item_id}')
    assert response.status_code == HTTP_200_OK
    assert_state_is_valid(response.json()['state'], 'Done')


@then('the item metadata are stored')
def check_metadata_is_stored(context: Context):
    response = context.test_client.get('/api/v1/items')
    assert response.status_code == HTTP_200_OK
    assert context.item_id in [item['id'] for item in response.json()]


@then("a telemetry message is stored")
def check_telemetry_message_is_stored(context):
    result = urlparse(context.postgres_db_uri)
    username, password, hostname, port = result.username, result.password, result.hostname, result.port
    database = result.path[1:]
    connection = psycopg2.connect(dbname=database, user=username, password=password,
                                  host=hostname, port=port)
    with connection.cursor() as curs:
        curs.execute('SELECT * FROM iothub.telemetry WHERE item_id = %s;', (context.item_id,))
        res = curs.fetchone()
    _id, device_id, decision, timestamp, item_id, config_res = res
    assert isinstance(_id, str)
    assert device_id.startswith('device_')
    assert Decision(decision)
    assert isinstance(timestamp, datetime)
    assert isinstance(item_id, str)
    assert config_res == 'station_config_TEST'
