from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict

from edge_orchestrator.domain.models.creds.aws_creds import AWSCreds
from edge_orchestrator.domain.models.creds.azure_creds import AzureCreds
from edge_orchestrator.domain.models.creds.gcp_creds import GCPCreds
from edge_orchestrator.domain.models.storage.storage_type import StorageType


class StorageConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    storage_type: StorageType = StorageType.FILESYSTEM
    target_directory: Path = Path("data_storage")
    prefix: Optional[str] = None
    cloud_storage_creds: Optional[Union[AWSCreds, AzureCreds, GCPCreds]] = None
