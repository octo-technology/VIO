import asyncio
import logging

from edge_orchestrator.application.config.config_manager import ConfigManager
from edge_orchestrator.application.use_cases.supervisor import Supervisor
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.ports.inspection_queue.i_inspection_queue import (
    IInspectionQueue,
)

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 0.05  # seconds


async def run_inspection_worker(
    queue: IInspectionQueue,
    supervisor: Supervisor,
    config_manager: ConfigManager,
) -> None:
    recovered = await queue.recover_interrupted()
    if recovered:
        logger.info("Recovered %d interrupted inspection(s)", recovered)

    while True:
        event = await queue.dequeue()
        if event is None:
            await asyncio.sleep(_POLL_INTERVAL)
            continue

        station_config = config_manager.get_config()
        if station_config is None:
            await queue.mark_failed(event.id, "no active station config")
            continue

        item = Item(id=event.item_id)
        try:
            await supervisor.inspect(item, station_config)
            await queue.mark_done(event.id)
        except Exception as exc:
            logger.exception("Inspection failed for event %s", event.id)
            await queue.mark_failed(event.id, str(exc))
