from typing import List, Optional

from pydantic import BaseModel

from models.edge import Edge


class EdgeDataManager(BaseModel):
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
