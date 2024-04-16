import os

from edge_orchestrator import logger


def load_config():
    configuration = os.environ.get("API_CONFIG", "default")
    logger.info(f"App running with configuration: {configuration}")

    available_configurations = [
        "test",
        "docker",
        "default",
        "edge",
        "edge-lite",
        "upload-gcp",
    ]
    if configuration not in available_configurations:
        raise ValueError(
            f"Unknown configuration '{configuration}'. " f"Valid configurations are {available_configurations}."
        )
    elif configuration == "test":
        from edge_orchestrator.environment.test import Test

        configuration_class = Test
    elif configuration == "docker":
        from edge_orchestrator.environment.docker import Docker

        configuration_class = Docker
    elif configuration == "local":
        from edge_orchestrator.environment.local import Local

        configuration_class = Local
    elif configuration == "default":
        from edge_orchestrator.environment.default import Default

        configuration_class = Default
    elif configuration == "edge":
        from edge_orchestrator.environment.edge_with_mongo_db_metadata_storage import (
            EdgeWithMongoDbMetadataStorage,
        )

        configuration_class = EdgeWithMongoDbMetadataStorage
    elif configuration == "edge-lite":
        from edge_orchestrator.environment.edge_with_azure_container_storage import (
            EdgeWithAzureContainerStorage,
        )

        configuration_class = EdgeWithAzureContainerStorage
    elif configuration == "upload-gcp":
        from edge_orchestrator.environment.upload_with_gcp_bucket import (
            UploadWithGCPBucket,
        )

        configuration_class = UploadWithGCPBucket

    return configuration_class()


config = load_config()


def get_metadata_storage():
    return config.get_metadata_storage()


def get_binary_storage():
    return config.get_binary_storage()


def get_model_forward():
    return config.get_model_forward()


def get_inventory():
    return config.get_inventory()


def get_station_config():
    return config.get_station_config()


def get_edge_station():
    return config.get_edge_station()


def get_telemetry_sink():
    return config.get_telemetry_sink()
