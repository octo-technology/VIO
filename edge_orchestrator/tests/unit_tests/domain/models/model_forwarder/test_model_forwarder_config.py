from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)


class TestModelForwarderConfig:

    def test_model_forwarder_config_minimal_fields_are_sufficient(self):
        # Given / When
        config = ModelForwarderConfig(
            model_name="marker_quality_control",
            model_version="1",
        )

        # Then
        assert config.model_id == "marker_quality_control_1"
        assert config.model_type is None
