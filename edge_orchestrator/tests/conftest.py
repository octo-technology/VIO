import os
import sys
from pathlib import Path

import pytest

from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_factory import (
    IModelForwarderFactory,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import (
    FakeModelForwarder,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_factory import (
    ModelForwarderFactory,
)
from edge_orchestrator.utils.singleton import SingletonMeta

pytest_plugins = [
    "fixtures.binaries",
    "fixtures.containers",
]

EDGE_MODEL_SERVING = {
    "image_name": "ghcr.io/octo-technology/vio/edge_model_serving:main",
    "container_volume_path": "/tf_serving",
    "host_volume_path_suffix": "edge_model_serving",
}
EDGE_TFLITE_SERVING_IMG = "ghcr.io/octo-technology/vio/edge_tflite_serving:main"

sys.path.append((Path(__file__).parent / "helpers").resolve())
os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"


@pytest.fixture(scope="function")
def mocked_model_forwarder_factory() -> IModelForwarderFactory:
    model_forwarder_factory = ModelForwarderFactory()
    model_forwarder_factory.create_model_forwarder = lambda config: FakeModelForwarder(config)
    return model_forwarder_factory


@pytest.fixture()
def cleanup_singleton():
    yield
    SingletonMeta._instances = {}
