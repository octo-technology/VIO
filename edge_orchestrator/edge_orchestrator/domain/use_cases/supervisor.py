import functools
import io
from abc import abstractmethod
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Union

from PIL import Image

from edge_orchestrator.api_config import (
    get_binary_storage,
    get_edge_station,
    get_metadata_storage,
    get_model_forward,
    get_station_config,
    get_telemetry_sink,
    logger,
)
from edge_orchestrator.domain.models.business_rule.camera_rule.camera_rule_factory import (
    get_camera_rule,
)
from edge_orchestrator.domain.models.business_rule.item_rule.item_rule_factory import (
    get_item_rule,
)
from edge_orchestrator.domain.models.camera import get_last_inference_by_camera
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.domain.models.supervisor_state import SupervisorState

def check_capture_according_to_config(item: Item, cameras: List[Dict]):
    binaries = set(item.binaries)
    cameras = set(cameras)
    missing_camera_binary = cameras.difference(binaries)
    if len(missing_camera_binary) != 0:
        logger.warning(f"Only {len(binaries)} were received and {len(cameras)} are expected!")
        logger.warning(f"Missing image for camera: {missing_camera_binary}")


class Supervisor:
    def __init__(
        self,
        metadata_storage=get_metadata_storage(),
        binary_storage=get_binary_storage(),
        model_forward=get_model_forward(),
        station_config=get_station_config(),
        edge_station=get_edge_station(),
        telemetry_sink=get_telemetry_sink(),
    ):
        self.metadata_storage = metadata_storage
        self.binary_storage = binary_storage
        self.model_forward = model_forward
        self.station_config = station_config
        self.edge_station = edge_station
        self.telemetry_sink = telemetry_sink

    def save_item_metadata(self, fct):
        @functools.wraps(fct)
        async def wrapper(item: Item, *args):
            item.state = args[0].value
            await fct(item)
            active_config_name = self.station_config.active_config["name"]
            self.metadata_storage.save_item_metadata(item, active_config_name)

        return wrapper

    async def inspect(self, item: Item):
        item.station_config = self.station_config.active_config_name
        if self.edge_station is not None:
            self.edge_station.register_cameras(self.station_config)

        tasks = OrderedDict()

        @self.save_item_metadata
        async def capture(item: Item):
            if item.binaries is None or len(item.binaries) == 0:
                cameras_metadata, binaries = self.edge_station.capture()
                item.cameras_metadata = cameras_metadata
                item.binaries = binaries
            check_capture_according_to_config(item, self.station_config.get_cameras())

        @self.save_item_metadata
        async def save_item_binaries(item: Item):
            self.binary_storage.save_item_binaries(item, self.station_config.active_config["name"])

        @self.save_item_metadata
        async def set_inferences(item: Item):
            item.inferences = await self.get_predictions(item)

        @self.save_item_metadata
        async def set_decision(item: Item):
            decision = self.apply_business_rules(item)
            item.decision = decision.value
            telemetry_msg = {
                "item_id": item.id,
                "config": item.station_config,
                "decision": decision.value,
            }

            await self.telemetry_sink.send(telemetry_msg)

        async def set_error_state(item: Item, error_message: str):
            item.error = True
            item.error_message = str(error_message)

        tasks[SupervisorState.CAPTURE] = capture
        tasks[SupervisorState.SAVE_BINARIES] = save_item_binaries
        tasks[SupervisorState.INFERENCE] = set_inferences
        tasks[SupervisorState.DECISION] = set_decision

        for supervisor_state, task_fct in tasks.items():
            logger.info(f"Starting {supervisor_state.value}")
            try:
                logger.info(f"Entering try {supervisor_state.value}")
                await task_fct(item, supervisor_state)
            except Exception as e:
                logger.error(f"Error during {supervisor_state.value}: {e}")
                await set_error_state(item, str(e))

            logger.info(f"End of {supervisor_state.value}")

        item.state = SupervisorState.DONE.value
        active_config_name = self.station_config.active_config["name"]
        self.metadata_storage.save_item_metadata(item, active_config_name)

    async def get_predictions(self, item: Item) -> Dict[str, Dict]:
        predictions = {}
        for camera_id in self.station_config.get_cameras():
            predictions_per_camera = await self.get_prediction_for_camera(camera_id, item, "full_image")
            predictions[camera_id] = predictions_per_camera
        return predictions

    async def get_prediction_for_camera(
        self, camera_id: str, item: Item, image_name: str
    ) -> Dict[str, Union[Dict, Any]]:
        inference_output = {}
        binary_data = item.binaries[camera_id]
        model_pipeline = self.station_config.get_model_pipeline_for_camera(camera_id)
        prediction_for_camera = await self.get_inference(inference_output, model_pipeline, binary_data, image_name)

        return prediction_for_camera

    async def get_inference(
        self,
        inference_output: Dict,
        model_pipeline: List[ModelInfos],
        full_image: bytes,
        image_name: str,
    ) -> Dict[str, Dict]:
        for current_model in model_pipeline:
            if _model_did_run(current_model.id, inference_output):
                continue
            logger.info(f"Getting inference for model {current_model.id}")
            if _model_has_no_dependency(current_model.depends_on):
                inference_output[current_model.id] = await self.model_forward.perform_inference(
                    current_model, full_image, image_name
                )
            else:
                inference_output[current_model.id] = {}
                model_dependencies = [
                    model_infos for model_infos in model_pipeline if model_infos.id in current_model.depends_on
                ]
                inference_output_dependencies = await self.get_inference(
                    inference_output, model_dependencies, full_image, image_name
                )
                for model_dependency in model_dependencies:
                    for (
                        object_id,
                        inference_output_dependency,
                    ) in inference_output_dependencies[
                        model_dependency.id
                    ].items():  # noqa
                        object_location = inference_output_dependency["location"]
                        cropped_image = crop_image(full_image, object_location)
                        inference_output_object = await self.model_forward.perform_inference(
                            current_model, cropped_image, object_id
                        )
                        for (
                            sub_object_id,
                            sub_object_info,
                        ) in inference_output_object.items():
                            if "location" in sub_object_info.keys():
                                sub_object_info["location"] = relocate_sub_object_location_within_full_image(
                                    object_location, sub_object_info["location"]
                                )
                            inference_output[current_model.id][sub_object_id] = sub_object_info

        return inference_output

    @abstractmethod
    def apply_business_rules(self, item: Item) -> Decision:
        camera_decisions = {}

        if item.inferences == Decision.NO_DECISION:
            return Decision.NO_DECISION

        else:
            for camera_id in item.inferences:
                camera_rule_name = self.station_config.active_config["cameras"][camera_id]["camera_rule"]["name"]
                camera_rule_parameters = self.station_config.active_config["cameras"][camera_id]["camera_rule"][
                    "parameters"
                ]

                last_model_inferences = get_last_inference_by_camera(item.inferences[camera_id])
                if last_model_inferences == Decision.NO_DECISION:
                    return Decision.NO_DECISION
                labels_of_last_model_inferences = get_labels(last_model_inferences)

                camera_rule = get_camera_rule(camera_rule_name, **camera_rule_parameters)
                camera_decision = camera_rule.get_camera_decision(labels_of_last_model_inferences)

                camera_decisions[camera_id] = camera_decision.value

            item_rule_name = self.station_config.active_config["item_rule"]["name"]
            item_rule_parameters = self.station_config.active_config["item_rule"]["parameters"]

            item_rule = get_item_rule(item_rule_name, **item_rule_parameters)
            item_decision = item_rule.get_item_decision(camera_decisions)

            return item_decision


def get_labels(inferences):
    inferences_labels = []
    objects_in_last_model = list(inferences.keys())
    for obj in objects_in_last_model:
        inferences_labels.append(inferences[obj]["label"])
    return inferences_labels


def _model_did_run(model_id: str, inference_output: Dict) -> bool:
    return model_id in inference_output.keys()


def _model_has_no_dependency(depends_on: List) -> bool:
    return len(depends_on) == 0


def crop_image(binary_data: bytes, detected_object: List[int]) -> bytes:
    xmin, ymin, xmax, ymax = detected_object
    if xmin <= xmax and ymin <= ymax:
        cropped_image = io.BytesIO()
        image = Image.open(io.BytesIO(binary_data))
        area = image.crop((xmin, ymin, xmax, ymax))
        if area.mode in ["RGBA", "P"]:
            area = area.convert("RGB")
        area.save(cropped_image, format="JPEG")
        return cropped_image.getvalue()
    else:
        logger.error("Informations for cropping are incorrect, the initial picture is used")
        if xmin > xmax:
            logger.error(f"xmin (={xmin}) is greater than xmax (={xmax})")
        elif ymin > ymax:
            logger.error(f"ymin (={ymin}) is greater than xmax (={ymax})")
        return binary_data


def relocate_sub_object_location_within_full_image(
    object_location: List[int], sub_object_location: List[int]
) -> List[int]:
    [x_min_o, y_min_o, x_max_o, y_max_o] = object_location
    [x_min_so, y_min_so, x_max_so, y_max_so] = sub_object_location
    return [
        x_min_so + x_min_o,
        y_min_so + y_min_o,
        x_max_so + x_min_o,
        y_max_so + y_min_o,
    ]
