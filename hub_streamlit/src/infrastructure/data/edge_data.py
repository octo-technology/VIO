from datetime import datetime
from typing import Dict, List, Optional

from PIL import Image
from pydantic import BaseModel, Field


class Camera(BaseModel):
    pictures: List[dict] = Field(default_factory=list)


# io.BytesIO


class Item(BaseModel):
    number_pictures: int = 0
    creation_date: datetime
    metadata: Optional[dict] = None
    camera_names: List[str] = Field(default_factory=list)
    cameras: Dict[str, Camera] = Field(default_factory=dict)


class UseCase(BaseModel):
    item_names: List[str] = Field(default_factory=list)
    items: Dict[str, Item] = Field(default_factory=dict)


class Edge(BaseModel):
    edge_ip: Optional[str] = None
    use_case_names: List[str] = Field(default_factory=list)
    use_cases: Dict[str, UseCase] = Field(default_factory=dict)


class EdgeData(BaseModel):
    edge_names: List[str] = Field(default_factory=list)
    edges: Dict[str, Edge] = Field(default_factory=dict)

    def add_edge(self, edge_name: str):
        self.edge_names.append(edge_name)
        self.edges[edge_name] = Edge()

    def add_usecase(self, edge_name: str, use_case: str, edge_ip: str):
        self.edges[edge_name].use_case_names.append(use_case)
        self.edges[edge_name].edge_ip = edge_ip
        self.edges[edge_name].use_cases[use_case] = UseCase()

    def add_item(
        self,
        edge_name: str,
        use_case: str,
        item_id: str,
        time_created: str,
        metadata: dict,
    ):
        self.edges[edge_name].use_cases[use_case].item_names.append(item_id)
        self.edges[edge_name].use_cases[use_case].items[item_id] = Item(
            creation_date=time_created,
            metadata=metadata,
        )

    def add_camera(self, edge_name: str, use_case: str, item_id: str, camera_id: str):
        self.edges[edge_name].use_cases[use_case].items[item_id].camera_names.append(
            camera_id
        )
        self.edges[edge_name].use_cases[use_case].items[item_id].cameras[
            camera_id
        ] = Camera()

    def add_picture(
        self,
        edge_name: str,
        use_case: str,
        item_id: str,
        camera_id: str,
        picture: Image,
    ):
        self.edges[edge_name].use_cases[use_case].items[item_id].cameras[
            camera_id
        ].pictures.append(picture)
        self.edges[edge_name].use_cases[use_case].items[item_id].number_pictures += 1
