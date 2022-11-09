import json
from typing import Dict

from supervisor.domain.ports.telemetry_sink import TelemetrySink
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message


class AzureIotHubTelemetrySink(TelemetrySink):

    def __init__(self):
        self.client = IoTHubModuleClient.create_from_edge_environment()

    async def send(self, message: Dict):
        message = json.dumps(message)
        await self.client.send_message(Message(message))
