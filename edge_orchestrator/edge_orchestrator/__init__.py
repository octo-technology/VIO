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

# TODO: define tracker
# ROOT_PATH = Path(__file__).parents[3]
# emissions_path = ROOT_PATH / "emissions"
# tracker = EmissionsTracker(project_name="detection_inference", measure_power_secs=1,
#                            tracking_mode="process", log_level="info", output_dir=str(emissions_path))