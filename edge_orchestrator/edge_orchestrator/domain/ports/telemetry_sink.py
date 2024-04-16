from abc import abstractmethod
from typing import Dict


class TelemetrySink:
    @abstractmethod
    async def send(self, message: Dict):
        pass
