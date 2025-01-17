from pydantic import BaseModel
from src.infrastructure.data.camera_data import CameraData


class ItemDataset(BaseModel):
    item_id: list = []
    camera_list: list[CameraData] = []
    number_of_pictures: int
    creation_date: str
    metadata: dict
