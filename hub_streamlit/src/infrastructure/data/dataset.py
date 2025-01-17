from typing import List
from pydantic import BaseModel
from src.infrastructure.data.edge_dataset import EdgeDataset


class Dataset(BaseModel):
    edges_names: list = []
    edges_list: list[EdgeDataset] = []

    def populate(self, blob_name_split: List[str]) -> None:
        blob_edge = blob_name_split[0]

        edge_dataset = self.get_edge_dataset(blob_edge)
        edge_dataset.populate(blob_name_split)

    def get_edge_dataset(self, edge_name: str) -> EdgeDataset:
        edge_dataset = next((edge for edge in self.edges_list if edge.edge_name == edge_name), None)

        if edge_dataset is None:
            edge_dataset = EdgeDataset(edge_name=edge_name)
            self.edges_list.append(edge_dataset)

        return edge_dataset
