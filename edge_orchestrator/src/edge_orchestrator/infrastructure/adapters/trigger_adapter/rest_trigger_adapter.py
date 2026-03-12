import asyncio

from edge_orchestrator.domain.ports.inspection_queue.i_inspection_queue import (
    IInspectionQueue,
)
from edge_orchestrator.domain.ports.trigger_adapter.i_trigger_adapter import (
    ITriggerAdapter,
)


class RestTriggerAdapter(ITriggerAdapter):
    """HTTP trigger adapter.

    Passive: enqueueing is handled by the POST /trigger FastAPI endpoint.
    This adapter's run() simply stays alive until cancelled, signalling that
    the REST trigger is active. Active adapters (MQTT, OPC UA) implement real
    event polling in run().
    """

    async def run(self, queue: IInspectionQueue) -> None:
        await asyncio.sleep(float("inf"))

    @classmethod
    def config_schema(cls) -> dict:
        return {
            "type": "object",
            "title": "RestTriggerConfig",
            "properties": {},
            "additionalProperties": False,
        }
