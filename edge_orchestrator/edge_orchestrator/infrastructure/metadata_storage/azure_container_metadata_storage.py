import json
import os
from typing import Dict, List
from datetime import datetime

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from smart_open import open

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.metadata_storage import MetadataStorage


class AzureContainerMetadataStorage(MetadataStorage):
    def __init__(self):
        self.azure_container_name = os.getenv('AZURE_CONTAINER_NAME')
        az_storage_connection_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self._blob_service_client = BlobServiceClient.from_connection_string(az_storage_connection_str)
        try:
            self._blob_service_client.create_container(self.azure_container_name)
        except ResourceExistsError:
            pass
        self._container_client = self._blob_service_client.get_container_client(self.azure_container_name)
        self._transport_params = {'client': self._blob_service_client}

    def save_item_metadata(self, item: Item):
        with open(f'azure://{self.azure_container_name}/{item.id}/metadata.json',
                  'wb', transport_params=self._transport_params) as f:
            f.write(json.dumps(item.get_metadata()).encode('utf-8'))

    def get_item_metadata(self, item_id: str) -> Dict:
        with open(f'azure://{self.azure_container_name}/{item_id}/metadata.json',
                  'rb', transport_params=self._transport_params) as f:
            return json.loads(f.read())

    def get_item_state(self, item_id: str) -> str:
        item_metadata = self.get_item_metadata(item_id)
        return item_metadata["state"]

    def get_all_items_metadata(self) -> List[Dict]:
        metadata = []
        for blob in self._container_client.list_blobs():
            if 'metadata.json' in blob['name']:
                with open(f'azure://{self.azure_container_name}/{blob["name"]}',
                          'rb', transport_params=self._transport_params) as f:
                    metadata.append(json.load(f))
                metadata.append(json.load(f))
        return metadata
