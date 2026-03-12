from abc import ABC, abstractmethod

from edge_orchestrator.domain.ports.inspection_queue.i_inspection_queue import IInspectionQueue


class ITriggerAdapter(ABC):
    @abstractmethod
    async def run(self, queue: IInspectionQueue) -> None:
        """Main loop: listen for trigger events and enqueue them.

        For active adapters (MQTT, OPC UA) this is a polling loop.
        For passive adapters (REST) this is a sentinel that stays alive until cancelled.
        Runs until cancelled via asyncio.CancelledError.
        """

    @classmethod
    @abstractmethod
    def config_schema(cls) -> dict:
        """Return the JSON Schema for this adapter's configuration block."""
