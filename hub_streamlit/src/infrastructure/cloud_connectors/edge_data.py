import numpy as np
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Camera(BaseModel):
    pictures: List[dict] = Field(default_factory=list)

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
