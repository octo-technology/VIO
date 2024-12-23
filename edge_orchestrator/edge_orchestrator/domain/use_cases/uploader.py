import functools
from collections import OrderedDict
from enum import Enum

from edge_orchestrator.api_config import (
    get_binary_storage,
    get_metadata_storage,
    logger,
)
from edge_orchestrator.domain.models.item import Item


class UploaderState(Enum):
    SAVE_BINARIES = "Save Binaries"
    DONE = "Done"


class Uploader:
    def __init__(
        self,
        metadata_storage=get_metadata_storage(),
        binary_storage=get_binary_storage(),
    ):
        self.metadata_storage = metadata_storage
        self.binary_storage = binary_storage

    def save_item_metadata(self, fct):
        @functools.wraps(fct)
        async def wrapper(item: Item, active_config_name: str, *args):
            item.state = args[0].value
            await fct(item)
            self.metadata_storage.save_item_metadata(item, active_config_name)

        return wrapper

    async def upload(self, item: Item, active_config_name: str):
        tasks = OrderedDict()

        @self.save_item_metadata
        async def save_item_binaries(item: Item):
            self.binary_storage.save_item_binaries(item, active_config_name)

        async def set_error_state(item: Item, error_message: str):
            item.error = True
            item.error_message = str(error_message)

        tasks[UploaderState.SAVE_BINARIES] = save_item_binaries

        for uploader_state, task_fct in tasks.items():
            logger.info(f"Starting {uploader_state.value}")
            try:
                logger.info(f"Entering try {uploader_state.value}")
                await task_fct(item, uploader_state)
            except Exception as e:
                logger.error(f"Error during {uploader_state.value}: {e}")
                await set_error_state(item, str(e))

            logger.info(f"End of {uploader_state.value}")

        item.state = UploaderState.DONE.value
        self.metadata_storage.save_item_metadata(item, active_config_name)
