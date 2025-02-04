from typing import List, Optional

from pydantic import BaseModel

from models.edge_data import EdgeData


class EdgeDataManager(BaseModel):
    edges: List[EdgeData] = []

    def add_edge(self, edge_data: EdgeData):
        self.edges.append(edge_data)

    def get_edge_names(self) -> List[str]:
        return [edge.name for edge in self.edges]

    def get_edge(self, name: str) -> Optional[EdgeData]:
        for edge in self.edges:
            if edge.name == name:
                return edge
        return None
