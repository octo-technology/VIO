import os

from hub_labelizer import logger


def load_config():
    configuration = os.environ.get("API_CONFIG", "default")
    logger.info(f"App running with configuration: {configuration}")

    available_configurations = [
        "default",
    ]

    if configuration not in available_configurations:
        raise ValueError(
            f"Unknown configuration '{configuration}'. "
            f"Valid configurations are {available_configurations}."
        )

        configuration_class = Docker
    elif configuration == "default":
        from hub_labelizer.environment.default import Default

        configuration_class = Default

    return configuration_class()


config = load_config()


def get_metadata_storage():
    return config.get_metadata_storage()


def get_binary_storage():
    return config.get_binary_storage()


def get_station_config():
    return config.get_station_config()


def get_labelizer():
    return config.get_labelizer()