from typing import Dict, List, Optional

from pydantic import BaseModel

from models.item import Item


class UseCase(BaseModel):
    name: str
    items: List[Item] = []

    def add_item(
        self,
        item_id: str,
        time_created: str,
        metadata: dict,
    ):
        self.items.append(Item(
            id=item_id,
            creation_date=time_created,
            metadata=metadata,
        ))

    def get_item_ids(self) -> List[str]:
        return [item.id for item in self.items]

    def get_item(self, item_id: str) -> Optional[Item]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None