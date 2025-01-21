from datetime import datetime
from typing import Dict, List, Optional

from PIL import Image
from pydantic import BaseModel, Field


class Camera(BaseModel):
    pictures: List[dict] = Field(default_factory=list)


class Item(BaseModel):
    number_pictures: int = 0
    creation_date: datetime
    metadata: Optional[dict] = None
    camera_names: List[str] = Field(default_factory=list)
    cameras: Dict[str, Camera] = Field(default_factory=dict)

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


class UseCase(BaseModel):
    item_names: List[str] = Field(default_factory=list)
    items: Dict[str, Item] = Field(default_factory=dict)

    def add_item(
        self,
        item_id: str,
        time_created: str,
        metadata: dict,
    ):
        self.item_names.append(item_id)
        self.items[item_id] = Item(
            creation_date=time_created,
            metadata=metadata,
        )


class Edge(BaseModel):
    edge_ip: Optional[str] = None
    use_case_names: List[str] = Field(default_factory=list)
    use_cases: Dict[str, UseCase] = Field(default_factory=dict)

    def add_usecase(self, use_case: str, edge_ip: str):
        self.edge_ip = edge_ip
        self.use_case_names.append(use_case)
        self.use_cases[use_case] = UseCase()


class EdgeData(BaseModel):
    edge_names: List[str] = Field(default_factory=list)
    edges: Dict[str, Edge] = Field(default_factory=dict)

    def add_edge(self, edge_name: str):
        self.edge_names.append(edge_name)
        self.edges[edge_name] = Edge()
