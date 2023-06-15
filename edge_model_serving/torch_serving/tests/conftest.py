import os
import requests
from pathlib import Path
import time

TEST_MODELS_FOLDER_PATH = Path(__file__).parents[1] / 'models/'
TEST_CONFIG_FOLDER_PATH = Path(__file__).parents[1] / 'config.properties'

def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    print('Launch torchserve before tests')
    os.system(
        f"torchserve --start --model-store {TEST_MODELS_FOLDER_PATH} --models yolo=yolo5.mar --ts-config {TEST_CONFIG_FOLDER_PATH}")
    time.sleep(10)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    print('Stop torchserve at the end of tests')
    os.system(f"torchserve --stop")