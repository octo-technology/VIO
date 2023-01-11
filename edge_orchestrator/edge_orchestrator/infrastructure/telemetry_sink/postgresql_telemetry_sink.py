from datetime import datetime
from random import randrange
from urllib.parse import urlparse
from uuid import uuid4

import psycopg2
import time
from typing import Dict

from edge_orchestrator import logger
from edge_orchestrator.domain.ports.telemetry_sink import TelemetrySink


class PostgresTelemetrySink(TelemetrySink):

    def __init__(self, connection_url: str, timeout: int = 30, interval: int = 2):
        self.connection_url = connection_url
        self._connection = None
        self._timeout = timeout
        self._interval = interval
        self._device_id = f'device_{randrange(42)}'

    @property
    def connection(self):
        if self._connection:
            return self._connection

        result = urlparse(self.connection_url)
        username, password, hostname, port = result.username, result.password, result.hostname, result.port
        database = result.path[1:]

        nb_retry = self._timeout // self._interval
        for i in range(nb_retry):
            try:
                self._connection = psycopg2.connect(dbname=database, user=username, password=password,
                                                    host=hostname, port=port)
                logger.debug(f'Telemetry Postgres DB took ‘{i * self._interval}‘sec to start and be migrated')
                return self._connection
            except psycopg2.OperationalError:
                time.sleep(self._interval)
        else:
            raise TimeoutError(f'Unable to connect to Telemetry Postgres DB using {self.connection_url} after {self._timeout:.0f} seconds')  # noqa

    async def send(self, message: Dict):
        try:
            _id = uuid4().__str__()
            device_id = self._device_id
            decision = message['decision']
            timestamp = datetime.now()
            item_id = message['item_id']
            config = message['config']

            self._insert_message(_id, device_id, decision, timestamp, item_id, config)
        except psycopg2.DatabaseError as e:
            logger.error(f'Message was not correctly inserted into telemetry table : {e}')

    def _insert_message(self, _id: str, device_id: str, decision: str, timestamp: datetime, item_id: str,
                        config: str):
        with self.connection.cursor() as curs:
            curs.execute(
                'INSERT INTO iothub.telemetry '
                '(id, device_id, business_decision, timestamp, item_id, config) VALUES (%s, %s, %s, %s, %s, %s)',
                (_id, device_id, decision, timestamp, item_id, config)
            )
        self.connection.commit()
        logger.warning(f'Telemetry message for item ‘{item_id}‘ stored with id ‘{_id}‘')
