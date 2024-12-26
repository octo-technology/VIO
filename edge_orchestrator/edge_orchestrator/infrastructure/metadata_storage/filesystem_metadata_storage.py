import json
from pathlib import Path
from typing import Dict, List

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage


class FileSystemMetadataStorage(MetadataStorage):
    def __init__(self, src_directory_path: Path, active_config_name: str):
        self.folder = src_directory_path
        self.active_config_name = active_config_name

    def save_item_metadata(self, item: Item):
        (self.folder / self.active_config_name / item.id).mkdir(parents=True, exist_ok=True)
        filepath = _get_filepath(self.folder, item.id, self.active_config_name)
        with filepath.open("w") as f:
            json.dump(item.get_metadata(), f)

    def get_item_metadata(self, item_id: str) -> Dict:
        filepath = _get_filepath(self.folder, item_id, self.active_config_name)
        with filepath.open("r") as f:
            item_metadata = json.load(f)
        return item_metadata

    def get_item_state(self, item_id: str) -> str:
        item_metadata = self.get_item_metadata(item_id)
        return item_metadata["state"]

    def get_all_items_metadata(self) -> List[Dict]:
        metadata = []
        for metadata_path in self.folder.glob("**/metadata.json"):
            with metadata_path.open("r") as f:
                metadata_item = json.load(f)
            metadata.append(metadata_item)
        return metadata


def _get_filepath(folder: Path, item_id: str, active_config_name: str, filename: str = "metadata.json") -> Path:
    return folder / active_config_name / item_id / filename
