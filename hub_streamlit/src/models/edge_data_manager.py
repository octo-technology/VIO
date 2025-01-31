from typing import List, Optional

from pydantic import BaseModel

from models.edge_data import EdgeData


class EdgeDataManager(BaseModel):
    edges: List[EdgeData] = []
    edge_names: List[str]

    def add_edge(self, edge_data: EdgeData):
        self.edges.append(edge_data)

    def get_edge_names(self) -> List[str]:
        return [edge.name for edge in self.edges]

    def get_edge_data(self, name: str) -> Optional[EdgeData]:
        for edge in self.edges:
            if edge.name == name:
                return edge
        return None
    
    # @st.cache_data(ttl=30)
    def refresh(self, gcp_client) -> None:
        for edge_name in self.edge_names:
            edge_data = EdgeData(name=edge_name)
            edge_data.get_ip(gcp_client)
            edge_data.extract(gcp_client=gcp_client)
            self.add_edge(edge_data)
    
    
