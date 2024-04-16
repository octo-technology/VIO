import json
import os
from pathlib import Path
from typing import Dict, List, Type, Union

from edge_orchestrator import logger
from edge_orchestrator.domain.models.camera import Camera
from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.domain.ports.inventory import Inventory
from edge_orchestrator.domain.ports.station_config import StationConfig
from edge_orchestrator.infrastructure.camera.fake_camera import FakeCamera
from edge_orchestrator.infrastructure.camera.raspberry_pi_camera import (
    RaspberryPiCamera,
)
from edge_orchestrator.infrastructure.camera.usb_camera import UsbCamera


class JsonStationConfig(StationConfig):
    def __init__(self, station_configs_folder: Path, inventory: Inventory, data_folder: Path):
        self.inventory = inventory
        self.data_folder = data_folder

        if not station_configs_folder.exists():
            raise FileNotFoundError(f'No station config folder found at "{station_configs_folder}"')

        self.station_configs_folder = station_configs_folder
        self.all_configs = {}
        self.load()

        self.active_config = None
        config_name = os.environ.get("ACTIVE_CONFIG_NAME", None)
        if config_name is not None:
            self.set_station_config(config_name)

    def load(self):
        self.all_configs = {}
        for config in self.station_configs_folder.glob("*.json"):
            with open(config, "r") as station_config_file:
                content = json.load(station_config_file)
                self.all_configs[config.with_suffix("").name] = content
            self._check_station_config_based_on_inventory(content)

    def set_station_config(self, config_name: str):
        try:
            self.active_config_name = config_name
            self.active_config = self.all_configs[self.active_config_name]
            logger.info(f"Activated the configuration {self.active_config_name}")
        except KeyError:
            raise KeyError(f"{config_name} is unknown. Valid configs are {list(self.all_configs.keys())}")

    def get_model_pipeline_for_camera(self, camera_id: str) -> List[ModelInfos]:
        model_pipeline = []
        model_pipeline_config = self.active_config["cameras"].get(camera_id)["models_graph"]
        if model_pipeline_config:
            for model_id, model in model_pipeline_config.items():
                model_infos = ModelInfos.from_model_graph_node(
                    camera_id, model_id, model, self.inventory, self.data_folder
                )
                model_pipeline.append(model_infos)
        else:
            logger.info(f'No models found for camera "{camera_id}"')
        return model_pipeline

    def get_cameras(self) -> List[str]:
        return list(self.active_config["cameras"].keys())

    def get_camera_type(self, camera_id: str) -> Type[Camera]:
        camera_config = self.active_config["cameras"].get(camera_id)
        if camera_config["type"] == "fake":
            return FakeCamera
        elif camera_config["type"] == "pi_camera":
            return RaspberryPiCamera
        elif camera_config["type"] == "usb_camera":
            return UsbCamera
        else:
            raise ValueError(f"Camera type ({camera_config['type']}) is not supported.")

    def get_camera_settings(self, camera_id: str) -> Dict[str, Union[str, int]]:
        camera_settings = {}
        camera_config = self.active_config["cameras"].get(camera_id)
        if camera_config:
            camera_settings["brightness"] = camera_config.get("brightness")
            camera_settings["exposition"] = camera_config.get("exposition")
            camera_settings["position"] = camera_config.get("position")
            camera_settings["source"] = camera_config.get("source")
        return camera_settings

    def _check_station_config_based_on_inventory(self, content):
        self._check_business_rule(content, "station")
        for camera_id, camera_conf in content["cameras"].items():
            camera_type = camera_conf["type"]
            if camera_type not in self.inventory.cameras:
                raise ValueError(f"Camera type {camera_type} is not supported.")
            self._check_business_rule(camera_conf, "camera")
            for model_id, model_conf in camera_conf["models_graph"].items():
                model = model_conf["name"]
                if model not in self.inventory.models:
                    raise ValueError(f"Model type {model} is not supported.")
                self._check_business_rule(model_conf, "model")

    def _check_business_rule(self, conf: Dict, conf_level: str):
        if "business_rule" in conf:
            business_rule = conf["business_rule"]
            if business_rule not in self.inventory.business_rules:
                raise ValueError(f"{conf_level.capitalize()} business rule ({business_rule}) is not supported.")
