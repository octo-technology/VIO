import datetime as dt
import random

import pytest
from freezegun import freeze_time

from edge_orchestrator.infrastructure.telemetry_sink.postgres_telemetry_sink import (
    PostgresTelemetrySink,
)


@pytest.mark.asyncio
class TestPostgresTelemetrySink:
    @freeze_time(
        lambda: dt.datetime(year=2023, month=1, day=27, hour=15, minute=0, second=0)
    )
    async def test_insert_and_select_query_given_one_telemetry_message(
        self, test_postgres_db_uri
    ):
        # Given
        telemetry_msg = {
            "decision": "OK",
            "item_id": "999-1b2-888",
            "config": "config1",
        }
        random.seed(42)
        telemetry_sink = PostgresTelemetrySink(test_postgres_db_uri)

        # When
        await telemetry_sink.send(telemetry_msg)

        # Then
        with telemetry_sink.connection.cursor() as curs:
            curs.execute("SELECT * FROM iothub.telemetry")
            res = curs.fetchone()
        _id, device_id, decision, timestamp, item_id, config_res = res
        assert device_id == "device_40"
        assert decision == "OK"
        assert timestamp == dt.datetime(2023, 1, 27, 15, 0)
        assert item_id == "999-1b2-888"
        assert config_res == "config1"

    def test_timeout_error_should_be_raised_with_no_postgresql_db(self):
        # Given
        vio = "postgresql://vio:vio@localhost:2345/vio"
        telemetry_sink = PostgresTelemetrySink(vio, timeout=2, interval=2)

        # When
        with pytest.raises(TimeoutError) as error:
            telemetry_sink.connection

        # Then
        assert (
            str(error.value)
            == "Unable to connect to Telemetry Postgres DB using postgresql://vio:vio@localhost:2345/vio "
            "after 2 seconds"
        )
