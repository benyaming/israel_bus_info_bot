from time import time
from logging import info

from celery import Celery
from redis import Redis
from utils_celery import update, update_last_updated_ts, delete_key_from_redis

import settings


# init redis params
app = Celery(
    'tasks',
    broker=f'amqp://{settings.RMQ_USER}:{settings.RMQ_PASS}@'
           f'{settings.RMQ_HOST}:{settings.RMQ_PORT}'
)


@app.task
def check_redis() -> None:
    """
    Task that runs periodically and scans redis for massages needs to be
    updated.
    :return:
    """
    info('CHECKING REDIS...')

    r = Redis(host=settings.R_HOST, port=settings.R_PORT,
              decode_responses=True)
    keys = r.keys()
    # check every key if it need to be updated
    for key in keys:
        expire = int(r.hget(key, 'expire'))
        data = r.hgetall(key)
        if int(time()) < expire:
            # keep updating
            updated_ts = int(data['updated'])
            if int(time()) - updated_ts > int(settings.PERIOD):
                update_last_updated_ts(key)
                update_message.delay(data)
        else:
            # init last update and delete key from redis
            send_last_update.delay(data)


@app.task(name='tasks.update_message')
def update_message(data: dict) -> None:
    """
    Task. Updates message
    :param data: dict with data for updating process
    :return:
    """
    info('UPDATING MESSAGE...')
    update(data)


@app.task
def send_last_update(data: dict):
    """
    Task. updates message last time and then deletes key from redis
    :param data:
    :return:
    """
    info('STOPPING MESSAGE TRACKING...')
    update(data, last_message=True)
    delete_key_from_redis(data['id'])


# celery beat config that schedules 'check_redis' task for every 5 seconds
app.conf.beat_schedule = {
    'check-redis': {
        'task': 'tasks.check_redis',
        'schedule': 5.0
    }
}
