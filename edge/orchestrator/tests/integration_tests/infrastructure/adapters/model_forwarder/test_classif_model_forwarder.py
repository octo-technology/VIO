import aiohttp
import pytest

from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder import (
    ModelForwarder,
)


class TestModelForwarderClassification:

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "model_name",
        [
            "marker_quality_control",
            "pin_detection",
        ],
    )
    async def test_model_forwarder_should_return_classif_prediction(
        self,
        model_name: str,
        setup_test_tflite_serving: str,
        marker_image: bytes,
    ):
        # Given
        model_forward_config = ModelForwarderConfig(
            model_name=model_name,
            model_version="1",
            model_serving_url=setup_test_tflite_serving,
        )
        model_forwarder = ModelForwarder(model_forward_config)

        # When
        actual_prediction = await model_forwarder.predict_on_binary(marker_image)

        # Then
        assert isinstance(actual_prediction, ClassifPrediction)
        assert actual_prediction.label in ["OK", "KO"]
        assert 0.0 <= actual_prediction.probability <= 1.0

    @pytest.mark.integration
    async def test_model_forwarder_should_raise_exception_with_bad_url_provided(
        self,
        setup_test_tflite_serving: str,
        marker_image: bytes,
    ):
        # Given
        model_forward_config = ModelForwarderConfig(
            model_name="marker_quality_control",
            model_version="1",
            model_serving_url=setup_test_tflite_serving,
        )
        model_forwarder = ModelForwarder(model_forward_config)
        model_forwarder._get_model_url = lambda: "http://bad_url"

        # When
        with pytest.raises(aiohttp.ClientError) as e:
            await model_forwarder.predict_on_binary(marker_image)

        # Then
        assert "Cannot connect to host" in str(e.value)
        assert e.type == aiohttp.ClientConnectorDNSError
