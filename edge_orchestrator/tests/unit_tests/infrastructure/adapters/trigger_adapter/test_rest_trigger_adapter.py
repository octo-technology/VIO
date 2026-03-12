import asyncio

from edge_orchestrator.domain.ports.trigger_adapter.i_trigger_adapter import (
    ITriggerAdapter,
)
from edge_orchestrator.infrastructure.adapters.trigger_adapter.rest_trigger_adapter import (
    RestTriggerAdapter,
)


def test_rest_trigger_adapter_implements_interface():
    assert issubclass(RestTriggerAdapter, ITriggerAdapter)


def test_config_schema_returns_valid_dict():
    schema = RestTriggerAdapter.config_schema()

    assert isinstance(schema, dict)
    assert schema["type"] == "object"
    assert "properties" in schema


async def test_run_is_cancellable():
    adapter = RestTriggerAdapter()
    queue = object()  # run() never interacts with the queue for REST

    task = asyncio.create_task(adapter.run(queue))
    await asyncio.sleep(0)  # yield so the task starts
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass  # expected

    assert task.done()
    assert task.cancelled()
