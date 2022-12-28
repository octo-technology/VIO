from abc import abstractmethod
from typing import Dict, List, Type, Union, Optional

from edge_orchestrator.domain.models.camera import Camera
from edge_orchestrator.domain.models.model_infos import ModelInfos


class StationConfig:

    all_configs: dict
    active_config_name: Optional[str]
    active_config: Optional[dict]

    @abstractmethod
    def get_model_pipeline_for_camera(self, camera_id: str) -> List[ModelInfos]:
        pass

    @abstractmethod
    def get_cameras(self) -> List[str]:
        pass

    @abstractmethod
    def get_camera_type(self, camera_id: str) -> Type[Camera]:
        pass

    @abstractmethod
    def get_camera_settings(self, camera_id: str) -> Dict[str, Union[str, int]]:
        pass

    @abstractmethod
    def set_station_config(self, config_name: str) -> None:
        pass
