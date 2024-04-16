import os
from typing import List

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from smart_open import open

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.binary_storage import BinaryStorage


class AzureContainerBinaryStorage(BinaryStorage):
    def __init__(self):
        self.azure_container_name = os.getenv("AZURE_CONTAINER_NAME")
        az_storage_connection_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self._blob_service_client = BlobServiceClient.from_connection_string(az_storage_connection_str)
        try:
            self._blob_service_client.create_container(self.azure_container_name)
        except ResourceExistsError:
            pass
        self._container_client = self._blob_service_client.get_container_client(self.azure_container_name)
        self._transport_params = {"client": self._blob_service_client}

    def save_item_binaries(self, item: Item, active_config_name: str):
        for camera_id, binary in item.binaries.items():
            with open(
                f"azure://{self.azure_container_name}/{active_config_name}/{item.id}_{camera_id}.jpg",
                "wb",
                transport_params=self._transport_params,
            ) as f:
                f.write(binary)

    def get_item_binary(self, item_id: str, camera_id: str, active_config_name: str) -> bytes:
        with open(
            f"azure://{self.azure_container_name}/{active_config_name}/{item_id}_{camera_id}.jpg",
            "rb",
            transport_params=self._transport_params,
        ) as f:
            return f.read()

    def get_item_binaries(self, item_id: str) -> List[str]:
        binaries = []
        for blob in self._container_client.list_blobs():
            if item_id in blob["name"]:
                with open(
                    f"azure://{self.azure_container_name}/{blob['name']}",
                    "rb",
                    transport_params=self._transport_params,
                ) as f:
                    binaries.append(f.read())
        return binaries

    def get_item_binary_filepath(
        self, item_id: str, camera_id: str, active_config_name: str
    ) -> str:
        return f"azure://{self.azure_container_name}/{active_config_name}/{item_id}_{camera_id}.jpg"
