from typing import Dict, List, Optional

from pydantic import BaseModel

from infrastructure.models.item import Item


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
