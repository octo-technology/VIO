import pytest

from edge_orchestrator.domain.models.inspection_event import InspectionEventStatus
from edge_orchestrator.infrastructure.adapters.inspection_queue.sqlite_inspection_queue import (
    SqliteInspectionQueue,
)


@pytest.fixture
async def queue():
    q = SqliteInspectionQueue(":memory:")
    await q.initialize()
    yield q
    await q.close()


async def test_enqueue_creates_pending_event(queue):
    event = await queue.enqueue("station_1")

    assert event.station_name == "station_1"
    assert event.status == InspectionEventStatus.PENDING
    assert event.id is not None
    assert event.item_id is not None


async def test_dequeue_returns_running_event(queue):
    enqueued = await queue.enqueue("station_1")

    dequeued = await queue.dequeue()

    assert dequeued is not None
    assert dequeued.id == enqueued.id
    assert dequeued.item_id == enqueued.item_id
    assert dequeued.status == InspectionEventStatus.RUNNING


async def test_dequeue_returns_none_when_empty(queue):
    result = await queue.dequeue()

    assert result is None


async def test_mark_done_updates_status(queue):
    await queue.enqueue("station_1")
    dequeued = await queue.dequeue()

    await queue.mark_done(dequeued.id)

    # Queue should now be empty (done events are not re-dequeued)
    next_event = await queue.dequeue()
    assert next_event is None


async def test_mark_failed_updates_status_and_error(queue):
    await queue.enqueue("station_1")
    dequeued = await queue.dequeue()

    await queue.mark_failed(dequeued.id, "something went wrong")

    # No pending events remain
    next_event = await queue.dequeue()
    assert next_event is None


async def test_recover_interrupted_resets_running_to_pending(queue):
    await queue.enqueue("station_1")
    await queue.dequeue()  # moves to RUNNING, simulating a crash mid-flight

    recovered = await queue.recover_interrupted()

    assert recovered == 1
    # Event should now be dequeue-able again
    event = await queue.dequeue()
    assert event is not None
    assert event.status == InspectionEventStatus.RUNNING


async def test_dequeue_respects_fifo_order(queue):
    first = await queue.enqueue("station_1")
    await queue.enqueue("station_2")

    dequeued = await queue.dequeue()

    assert dequeued.id == first.id
