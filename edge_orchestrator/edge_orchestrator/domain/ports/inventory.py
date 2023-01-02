from typing import List, Dict, Union


class Inventory:
    cameras: List[str]
    models: Dict[str, Dict[str, Union[str, int]]]
    camera_rules: List[str]
    item_rules: List[str]
