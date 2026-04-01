from typing import List, Optional

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
        self.items.append(
            Item(
                id=item_id,
                creation_date=time_created,
                metadata=metadata,
            )
        )

    def remove_item(self, item_id: str):
        for idx, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(idx)
                break

    def get_item_ids(self) -> List[str]:
        return [item.id for item in self.items]

    def get_item(self, item_id: str) -> Optional[Item]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None
