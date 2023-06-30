import json
from typing import Dict

from azure.iot.device import Message
from azure.iot.device.aio import IoTHubModuleClient

from edge_orchestrator.domain.ports.telemetry_sink import TelemetrySink


class AzureIotHubTelemetrySink(TelemetrySink):
    def __init__(self):
        self.client = IoTHubModuleClient.create_from_edge_environment()

    async def send(self, message: Dict):
        message = json.dumps(message)
        await self.client.send_message(Message(message))
