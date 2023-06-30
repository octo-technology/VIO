from abc import abstractmethod


class TelemetrySink:
    @abstractmethod
    async def send(self, message: str):
        pass
