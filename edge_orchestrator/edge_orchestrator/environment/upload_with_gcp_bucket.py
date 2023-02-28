from edge_orchestrator.environment.config import Config
from edge_orchestrator.infrastructure.binary_storage.gcp_binary_storage import (
    GCPBinaryStorage,
)
from edge_orchestrator.infrastructure.metadata_storage.gcp_metadata_storage import (
    GCPMetadataStorage,
)


class UploadWithGCPBucket(Config):

    def __init__(self):
        self.metadata_storage = GCPMetadataStorage()
        self.binary_storage = GCPBinaryStorage()
