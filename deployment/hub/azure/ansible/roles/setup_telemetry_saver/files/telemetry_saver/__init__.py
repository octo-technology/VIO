import json
import logging
import os
from base64 import b64decode

import azure.functions as func
import psycopg2


def main(event: func.EventGridEvent):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.info('Python EventGrid trigger processed an event: %s', result)

    msg_dict = json.loads(b64decode(event.get_json()['body']).decode())

    try:
        write(event.id,
              event.get_json()['systemProperties']['iothub-connection-device-id'],
              msg_dict['item_id'],
              msg_dict['config'],
              msg_dict['decision'],
              event.get_json()['systemProperties']['iothub-enqueuedtime'])
    except Exception as e:
        logging.info('Skipped write')
        logging.info(e)


def write(event_id, device_id, item_id, config, business_decision, timestamp):
    conn = connect()
    with conn:
        with conn.cursor() as curs:
            curs.execute(
                f"INSERT INTO iothub.telemetry (id, device_id, item_id, config, business_decision, timestamp) VALUES ('{event_id}', '{device_id}', '{item_id}','{config}', '{business_decision}', '{timestamp}');"
            )
    conn.close()


def connect():
    return psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
