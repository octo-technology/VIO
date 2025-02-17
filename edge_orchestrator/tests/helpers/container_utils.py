import logging
import os
from typing import Dict, Tuple, Union

import docker
from helpers.tf_serving_container import TfServingContainer
from testcontainers.core.container import DockerContainer

EDGE_MODEL_SERVING = {
    "image_name": "ghcr.io/octo-technology/vio/edge_model_serving:main",
    "container_volume_path": "/tf_serving",
    "host_volume_path_suffix": "edge_model_serving",
}
EDGE_TFLITE_SERVING_IMG = "ghcr.io/octo-technology/vio/edge_tflite_serving:main"


def check_image_presence_or_pull_it_from_registry(image_name: str):
    client = docker.from_env()
    image_tags = [tag for image in client.images.list() for tag in image.tags]
    if image_name not in image_tags:
        auth_config = None
        logging.debug(f"Pulling docker image {image_name} from registry when running tests for the first time...")
        if image_name.startswith("ghcr.io/octo-technology"):
            if os.getenv("REGISTRY_USERNAME") and os.getenv("REGISTRY_PASSWORD"):
                auth_config = {
                    "username": os.getenv("REGISTRY_USERNAME"),
                    "password": os.getenv("REGISTRY_PASSWORD"),
                }
            else:
                raise PermissionError(
                    "Please set your registry credentials with the following env vars: "
                    "REGISTRY_USERNAME & REGISTRY_PASSWORD"
                )
        client.images.pull(image_name, auth_config=auth_config)


def start_test_tf_serving(
    image_name: str,
    starting_log: str,
    env_vars: Dict[str, str],
    tf_serving_host: Union[str, None] = os.getenv("TENSORFLOW_SERVING_HOST"),
    tf_serving_port: Union[int, None] = os.getenv("TENSORFLOW_SERVING_PORT"),
    host_volume_path: str = None,
    container_volume_path: str = None,
) -> Tuple[str, TfServingContainer]:
    container = None
    if tf_serving_host is None or tf_serving_port is None:
        port_to_expose = 8501
        check_image_presence_or_pull_it_from_registry(image_name)
        container = TfServingContainer(
            image=image_name,
            port_to_expose=port_to_expose,
            env=env_vars,
            host_volume_path=host_volume_path,
            container_volume_path=container_volume_path,
        )
        container.start(starting_log)
        tf_serving_host = "0.0.0.0"
        # tf_serving_host = container.get_container_host_ip()
        tf_serving_port = container.get_exposed_port(port_to_expose)

    return f"http://{tf_serving_host}:{tf_serving_port}/", container


def stop_test_container(container: DockerContainer):
    if container:
        container.stop()
