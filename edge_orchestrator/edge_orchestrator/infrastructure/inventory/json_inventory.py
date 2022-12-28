import json
from pathlib import Path
from typing import List, Dict, Union

from edge_orchestrator.domain.ports.inventory import Inventory


class JsonInventory(Inventory):

    def __init__(self, inventory_path: Path):
        if not inventory_path.exists():
            raise FileNotFoundError(f'No inventory file found at "{inventory_path}"')

        with open(inventory_path, 'r') as inventory_file:
            content = json.load(inventory_file)
            self.cameras = content['cameras']
            self.models = content['models']
            self.camera_rules = content['camera_rules']
            self.item_rules = content['item_rules']

    def get_cameras(self) -> List[str]:
        return self.inventory['cameras']

    def get_models(self) -> Dict[str, Dict[str, Union[str, int]]]:
        return self.inventory['models']

    def get_camera_rules(self) -> List[str]:
        return self.inventory['camera_rules']

    def get_item_rules(self) -> List[str]:
        return self.inventory['item_rules']
