from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from models.camera import Camera
from models.decision import Decision


class Item(BaseModel):
    id: str
    number_pictures: int = 0
    creation_date: datetime
    metadata: Optional[Dict] = None
    cameras: List[Camera] = []

    def add_camera(self, camera_id: str):
        self.cameras.append(Camera(id=camera_id))

    def get_camera_ids(self) -> List[str]:
        return [camera.id for camera in self.cameras]

    def get_camera(self, camera_id: str) -> Optional[Camera]:
        for camera in self.cameras:
            if camera.id == camera_id:
                return camera
        return None

    def contains_predictions(self, camera_id: str) -> bool:
        if self.metadata is None or self.metadata == {}:
            return False

        metadata_inferences = self.metadata.get("inferences")
        if metadata_inferences is None or metadata_inferences == {}:
            return False

        for model_results in metadata_inferences[camera_id].values():
            if model_results == Decision.NO_DECISION.value or model_results == {}:
                return False
            for prediction in model_results.values():
                if "location" not in prediction:
                    return False
        return True
