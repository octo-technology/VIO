from pydantic import BaseModel
from src.infrastructure.data.item_dataset import ItemDataset


class UseCaseDataset(BaseModel):
    use_case_names: list = []
    item_list: list[ItemDataset] = []
