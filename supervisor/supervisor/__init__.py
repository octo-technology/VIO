import logging
from logging.config import fileConfig

from pkg_resources import resource_filename

fileConfig(resource_filename("supervisor", "logger.cfg"), disable_existing_loggers=False, defaults={
    "supervisor_level": "INFO",
    "supervisor_formatter": "classic"
})
logger = logging.getLogger("supervisor")
