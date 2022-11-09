import os

from supervisor import logger


def load_config():
    configuration = os.environ.get('API_CONFIG', 'default')
    logger.info(f'App running with configuration: {configuration}')

    available_configurations = ['test', 'docker', 'default', 'edge', 'edge-lite']
    if configuration not in available_configurations:
        raise ValueError(f"Unknown configuration '{configuration}'. "
                         f'Valid configurations are {available_configurations}.')
    elif configuration == 'test':
        from supervisor.environment.test import Test
        configuration_class = Test
    elif configuration == 'docker':
        from supervisor.environment.docker import Docker
        configuration_class = Docker
    elif configuration == 'default':
        from supervisor.environment.default import Default
        configuration_class = Default
    elif configuration == 'edge':
        from supervisor.environment.edge_with_mongo_db_metadata_storage import EdgeWithMongoDbMetadataStorage
        configuration_class = EdgeWithMongoDbMetadataStorage
    elif configuration == 'edge-lite':
        from supervisor.environment.edge_with_azure_container_storage import EdgeWithAzureContainerStorage
        configuration_class = EdgeWithAzureContainerStorage

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
