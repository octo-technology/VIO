from functools import lru_cache
from typing import Dict, Type, Optional, Any

from edge_orchestrator.domain.ports.telemetry_sink import TelemetrySink
from edge_orchestrator.infrastructure.telemetry_sink.azure_iot_hub_telemetry_sink import (
    AzureIotHubTelemetrySink,
)
from edge_orchestrator.infrastructure.telemetry_sink.fake_telemetry_sink import (
    FakeTelemetrySink,
)
from edge_orchestrator.infrastructure.telemetry_sink.postgres_telemetry_sink import (
    PostgresTelemetrySink,
)

AVAILABLE_TELEMETRY_SINK: Dict[str, Type[TelemetrySink]] = {
    "azure_iot_hub": AzureIotHubTelemetrySink,
    "fake": FakeTelemetrySink,
    "postgres": PostgresTelemetrySink,
}


class TelemetrySinkFactory:
    @staticmethod
    @lru_cache()
    def get_telemetry_sink(
        telemetry_sink_type: Optional[str] = "fake",
        **telemetry_sink_config: Optional[Dict[str, Any]],
    ) -> TelemetrySink:
        try:
            return AVAILABLE_TELEMETRY_SINK[telemetry_sink_type](
                **telemetry_sink_config
            )
        except KeyError as err:
            raise ValueError(
                f"Unknown telemetry sink type: {telemetry_sink_type}"
            ) from err
