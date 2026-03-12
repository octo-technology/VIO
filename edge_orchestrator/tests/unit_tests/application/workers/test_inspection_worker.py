import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from edge_orchestrator.application.workers.inspection_worker import (
    run_inspection_worker,
)
from edge_orchestrator.infrastructure.adapters.inspection_queue.sqlite_inspection_queue import (
    SqliteInspectionQueue,
)


@pytest.fixture
async def queue():
    q = SqliteInspectionQueue(":memory:")
    await q.initialize()
    yield q
    await q.close()


def _make_station_config():
    from edge_orchestrator.domain.models.station_config import StationConfig
    from edge_orchestrator.domain.models.storage.storage_config import StorageConfig

    return StationConfig(
        station_name="station_1",
        camera_configs={},
        binary_storage_config=StorageConfig(),
        metadata_storage_config=StorageConfig(),
    )


async def _run_worker_once(queue, supervisor, config_manager):
    """Run the worker until it processes one event or hits an empty queue, then cancel."""
    task = asyncio.create_task(run_inspection_worker(queue, supervisor, config_manager))
    await asyncio.sleep(0.3)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def test_worker_processes_enqueued_event(queue):
    supervisor = MagicMock()
    supervisor.inspect = AsyncMock()
    config_manager = MagicMock()
    config_manager.get_config.return_value = _make_station_config()

    event = await queue.enqueue("station_1")

    await _run_worker_once(queue, supervisor, config_manager)

    supervisor.inspect.assert_awaited_once()
    called_item = supervisor.inspect.call_args[0][0]
    assert called_item.id == event.item_id


async def test_worker_marks_event_done_on_success(queue):
    supervisor = MagicMock()
    supervisor.inspect = AsyncMock()
    config_manager = MagicMock()
    config_manager.get_config.return_value = _make_station_config()

    await queue.enqueue("station_1")

    await _run_worker_once(queue, supervisor, config_manager)

    # Queue should be empty (no more pending events)
    next_event = await queue.dequeue()
    assert next_event is None


async def test_worker_marks_event_failed_on_exception(queue):
    supervisor = MagicMock()
    supervisor.inspect = AsyncMock(side_effect=RuntimeError("camera error"))
    config_manager = MagicMock()
    config_manager.get_config.return_value = _make_station_config()

    await queue.enqueue("station_1")

    await _run_worker_once(queue, supervisor, config_manager)

    supervisor.inspect.assert_awaited_once()
    # No pending events left
    next_event = await queue.dequeue()
    assert next_event is None


async def test_worker_marks_failed_when_no_station_config(queue):
    supervisor = MagicMock()
    supervisor.inspect = AsyncMock()
    config_manager = MagicMock()
    config_manager.get_config.return_value = None

    await queue.enqueue("station_1")

    await _run_worker_once(queue, supervisor, config_manager)

    supervisor.inspect.assert_not_awaited()


async def test_worker_recovers_interrupted_events_on_startup(queue):
    # Simulate a previous crash: event stuck in RUNNING
    await queue.enqueue("station_1")
    await queue.dequeue()  # moves to RUNNING

    supervisor = MagicMock()
    supervisor.inspect = AsyncMock()
    config_manager = MagicMock()
    config_manager.get_config.return_value = _make_station_config()

    await _run_worker_once(queue, supervisor, config_manager)

    # Worker should have recovered and processed the event
    supervisor.inspect.assert_awaited_once()
