from enum import Enum


class StorageType(str, Enum):
    FILESYSTEM = "filesystem"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
