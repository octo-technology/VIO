from supervisor.domain.ports.telemetry_sink import TelemetrySink


class FakeTelemetrySink(TelemetrySink):

    async def send(self, message: str):
        pass
