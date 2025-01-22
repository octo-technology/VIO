from datetime import datetime
from typing import Dict, List, Optional

from PIL import Image
from pydantic import BaseModel

from infrastructure.models.camera import Camera
from infrastructure.models.decision import Decision


class Item(BaseModel):
    number_pictures: int = 0
    creation_date: datetime
    metadata: Optional[dict] = None
    camera_names: Optional[List[str]] = []
    cameras: Optional[Dict[str, Camera]] = {}

    def add_camera(self, camera_id: str):
        self.camera_names.append(camera_id)
        self.cameras[camera_id] = Camera()

    def add_picture(
        self,
        camera_id: str,
        picture: Image,
    ):
        self.cameras[camera_id].pictures.append(picture)
        self.number_pictures += 1

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
