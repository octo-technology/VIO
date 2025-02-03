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
    async def test_classif_model_forwarder_should_return_classif_pre(
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
            image_resolution=image_resolution,
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
    async def test_classif_model_forwarder_should_return_no_decision_with_bad_model_serving_url(
        self,
        setup_test_tflite_serving: str,
        marker_image: bytes,
        caplog,
    ):
        # Given
        image_resolution = ImageResolution(width=224, height=224)
        model_forward_config = ModelForwarderConfig(
            model_name=ModelName.marker_quality_control,
            model_type=ModelType.classification,
            model_version="1",
            class_names=["OK", "KO"],
            model_serving_url=setup_test_tflite_serving,
            image_resolution=image_resolution,
        )
        model_fowarder = ClassifModelForwarder(model_forward_config)
        model_fowarder._get_model_url = lambda: "http://bad_url"

        # When
        with caplog.at_level("ERROR"):
            actual_prediction = await model_fowarder.predict_on_binary(marker_image)

        # Then
        records = [(record.message, record.exc_info) for record in caplog.records]
        assert len(records) == 1
        actual_record = records[0]
        assert actual_record[0] == "Error while trying to get prediction from model, returning no decision prediction"
        assert issubclass(actual_record[1][0], aiohttp.ClientError)
        assert actual_prediction.label is None
