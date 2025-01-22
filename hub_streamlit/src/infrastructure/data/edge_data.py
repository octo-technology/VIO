from datetime import datetime
from typing import Dict, List, Optional

from PIL import Image
from pydantic import BaseModel


class Camera(BaseModel):
    pictures: Optional[List[dict]] = []


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


class UseCase(BaseModel):
    item_names: Optional[List[str]] = []
    items: Optional[Dict[str, Item]] = {}

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
    name: str
    edge_ip: Optional[str] = None
    use_case_names: Optional[List[str]] = []
    use_cases: Optional[Dict[str, UseCase]] = {}

    def add_usecase(self, use_case: str, edge_ip: str):
        self.edge_ip = edge_ip
        self.use_case_names.append(use_case)
        self.use_cases[use_case] = UseCase()


class EdgeData(BaseModel):
    edges: Optional[List[Edge]] = []

    def add_edge(self, edge_name: str):
        self.edges.append(Edge(name=edge_name))

    def get_edge_names(self) -> List[str]:
        return [edge.name for edge in self.edges]

    def get_edge(self, name: str) -> Optional[Edge]:
        for edge in self.edges:
            if edge.name == name:
                return edge
        return None
