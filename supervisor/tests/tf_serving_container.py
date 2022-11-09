from typing import Dict

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class TfServingContainer(DockerContainer):

    def __init__(self, image: str, port_to_expose: int, env: Dict, host_volume_path: str = None,
                 container_volume_path: str = None):
        super(TfServingContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        for key, value in env.items():
            self.with_env(key, value)
        if host_volume_path and container_volume_path:
            self.with_volume_mapping(host=host_volume_path, container=container_volume_path)

    @wait_container_is_ready()
    def _connect(self, default_starting_log: str):
        wait_for_logs(self, default_starting_log, timeout=10)

    def start(self, starting_log: str = r'Uvicorn running on'):
        super().start()
        self._connect(starting_log)
        return self
