import aiohttp
import pytest

from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ImageResolution,
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.classif_model_forwarder import (
    ClassifModelForwarder,
)


class TestClassifModelForwarder:

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "model_name,probability",
        [
            (ModelName.marker_quality_control, 0.83054119348526),
            (ModelName.pin_detection, 0.9996249675750732),
        ],
    )
    async def test_classif_model_forwarder_should_return_classif_prediction(
        self,
        model_name: ModelName,
        probability: float,
        setup_test_tflite_serving: str,
        marker_image: bytes,
    ):
        # Given
        image_resolution = ImageResolution(width=224, height=224)
        model_forward_config = ModelForwarderConfig(
            model_name=model_name,
            model_type=ModelType.classification,
            model_version="1",
            class_names=["OK", "KO"],
            model_serving_url=setup_test_tflite_serving,
            expected_image_resolution=image_resolution,
        )
        model_fowarder = ClassifModelForwarder(model_forward_config)

        expected_prediction = ClassifPrediction(
            prediction_type=PredictionType.class_, label="KO", probability=probability
        )

        # When
        actual_prediction = await model_fowarder.predict_on_binary(marker_image)

        # Then
        assert isinstance(actual_prediction, ClassifPrediction)
        assert actual_prediction == expected_prediction

    @pytest.mark.integration
    async def test_classif_model_forwarder_should_raise_exception_with_bad_url_provided(
        self,
        setup_test_tflite_serving: str,
        marker_image: bytes,
    ):
        # Given
        image_resolution = ImageResolution(width=224, height=224)
        model_forward_config = ModelForwarderConfig(
            model_name=ModelName.marker_quality_control,
            model_type=ModelType.classification,
            model_version="1",
            class_names=["OK", "KO"],
            model_serving_url=setup_test_tflite_serving,
            expected_image_resolution=image_resolution,
        )
        model_fowarder = ClassifModelForwarder(model_forward_config)
        model_fowarder._get_model_url = lambda: "http://bad_url"

        # When
        with pytest.raises(aiohttp.ClientError) as e:
            await model_fowarder.predict_on_binary(marker_image)

        # Then
        assert "nodename nor servname provided, or not known" in str(e.value)
        assert e.type == aiohttp.ClientConnectorDNSError
