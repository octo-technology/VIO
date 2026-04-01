import logging
from logging.config import fileConfig

from pkg_resources import resource_filename

fileConfig(
    fname=resource_filename("hub_labelizer", "logger.cfg"),
    disable_existing_loggers=False,
    defaults={
        "hub_labelizer_level": "INFO",
        "hub_labelizer_formatter": "classic",
    },
)

logger = logging.getLogger("hub_labelizer")
