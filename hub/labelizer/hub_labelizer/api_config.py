import os

from hub_labelizer import logger


def load_config():
    configuration = os.getenv("API_CONFIG", "default")
    logger.info(f"App running with configuration: {configuration}")

    available_configurations = ["default", "docker"]

    if configuration not in available_configurations:
        raise ValueError(
            f"Unknown configuration '{configuration}'. "
            f"Valid configurations are {available_configurations}."
        )

    elif configuration == "default":
        from hub_labelizer.environment.default import Default

        configuration_class = Default

    elif configuration == "docker":
        from hub_labelizer.environment.docker import Docker

        configuration_class = Docker

    return configuration_class()


config = load_config()


def get_labelizer():
    return config.get_labelizer()
