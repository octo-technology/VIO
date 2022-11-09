import os
from pathlib import Path

os.environ['API_CONFIG'] = 'test'
TEST_DATA_FOLDER_PATH = Path(__file__).parent / 'data'
TEST_CONFIG_FOLDER_PATH = Path(__file__).parent / 'config'
TEST_STATION_CONFIGS_FOLDER_PATH = TEST_CONFIG_FOLDER_PATH / 'station_configs'
TEST_STATION_CONFIG_PATH = TEST_STATION_CONFIGS_FOLDER_PATH / 'station_config_TEST.json'
TEST_STATION_CONFIG_2_PATH = TEST_STATION_CONFIGS_FOLDER_PATH / 'station_config_TEST2.json'
TEST_INVENTORY_PATH = TEST_CONFIG_FOLDER_PATH / 'inventory_TEST.json'
ROOT_REPOSITORY_PATH = Path(__file__).parents[2]

pytest_plugins = ['tests.fixtures.binaries', 'tests.fixtures.cameras_metadata',
                  'tests.fixtures.items', 'tests.fixtures.metadata',
                  'tests.fixtures.containers', 'tests.fixtures.items_config']
