from pathlib import Path

import pytest
from pydantic import ValidationError

from edge_orchestrator.domain.models.model_forwarder.image_resolution import (
    ImageResolution,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from tests.fixtures.containers import setup_test_tflite_serving


class TestModelForwarderConfig:

    def test_model_fowarder_config_should_raise_exception_of_class_names_path_does_not_exist(self):
        # Given
        class_names_filepath = Path("unexisting/path/labels.txt")

        # When
        with pytest.raises(ValidationError) as e:
            ModelForwarderConfig(
                model_name=ModelName.marker_quality_control,
                model_type=ModelType.classification,
                class_names_path=class_names_filepath,
                model_serving_url=setup_test_tflite_serving,
                expected_image_resolution=ImageResolution(width=224, height=224),
            )

        # Then
        assert f"Class names file {class_names_filepath} does not exist" in str(e.value)
