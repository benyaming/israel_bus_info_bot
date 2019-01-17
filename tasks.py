from time import time

from celery import Celery
from redis import Redis
from utils_celery import update, update_last_updated_ts, \
    set_expired, delete_key_from_redis

import settings


app = Celery(
    'tasks',
    broker=f'amqp://{settings.RMQ_USER}:{settings.RMQ_PASS}@'
           f'{settings.RMQ_HOST}:{settings.RMQ_PORT}'
)


@app.task
def check_redis():
    print('CHECKING REDIS...')
    r = Redis(host=settings.R_HOST, port=settings.R_PORT)
    keys = r.keys()
    for key in keys:
        expire = int(r.hget(key, 'expire').decode())
        data = {
            'id': int(r.hget(key, 'id').decode()),
            'message_id': int(r.hget(key, 'message_id').decode()),
            'station': int(r.hget(key, 'station').decode())
        }
        if int(time()) < expire:
            updated_ts = int(r.hget(key, 'updated').decode())
            if int(time()) - updated_ts > int(settings.PERIOD):
                update_last_updated_ts(key)
                update_message.delay(data)
        else:
            send_last_update.delay(data)


@app.task(name='tasks.update_message')
def update_message(data: dict):
    print('UPDATING MESSAGE...')
    update(data)


@app.task
def send_last_update(data: dict):
    print('STOPPING MESSAGE TRACKING...')
    update(data, last_message=True)
    delete_key_from_redis(data['id'])


app.conf.beat_schedule = {
    'check-redis': {
        'task': 'tasks.check_redis',
        'schedule': 5.0
    }
}
