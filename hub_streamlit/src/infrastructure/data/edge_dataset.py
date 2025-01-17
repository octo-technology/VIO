from pydantic import BaseModel
from src.infrastructure.data.usecase_dataset import UseCaseDataset


class EdgeDataset(BaseModel):
    edge_name: str
    use_case_list: list[UseCaseDataset] = []
    edge_ip: str
