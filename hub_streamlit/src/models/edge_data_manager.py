from typing import List, Optional

from pydantic import BaseModel

from models.edge_data import EdgeData


class EdgeDataManager(BaseModel):
    edges_data: List[EdgeData] = []

    def add_edge_data(self, edge_data: EdgeData):
        self.edges_data.append(edge_data)

    def get_edges_data_names(self) -> List[str]:
        return [edge.name for edge in self.edges_data]

    def get_edge_data(self, name: str) -> Optional[EdgeData]:
        for edge in self.edges_data:
            if edge.name == name:
                return edge
        return None
