import logging
from logging.config import fileConfig

from pkg_resources import resource_filename

fileConfig(
    fname=resource_filename("edge_orchestrator", "logger.cfg"),
    disable_existing_loggers=False,
    defaults={
        "edge_orchestrator_level": "INFO",
        "edge_orchestrator_formatter": "classic",
    },
)

logger = logging.getLogger("edge_orchestrator")
