from json import dumps
from time import time

from requests import get
from redis import Redis

from bus_api_celery import get_lines
from settings import TOKEN, R_HOST, R_PORT


def update(data: dict, last_message=False):
    bus_data = get_lines(data['station'])
    response = bus_data if not last_message else \
        f'{bus_data}\n\n*Message not updating!*'
    params = {
        'chat_id': data['user_id'],
        'message_id': data['message_id'],
        'parse_mode': 'Markdown',
        'text': response
    }
    keyboard = dumps(
        {
            "inline_keyboard": [
                [{"text": "Stop updating", "callback_data": "::"}]]
        }
    ) if not last_message else None
    if keyboard:
        params['reply_markup'] = keyboard
    print('SENDING REQUEST TO TELEGRAM API...')
    url = f'https://api.telegram.org/bot{TOKEN}/editmessagetext'
    r = get(url, params)
    print(r.status_code)


def update_last_updated_ts(key: str):
    r = Redis(R_HOST, R_PORT)
    r.hset(key, 'updated', int(time()))


def set_expired(key: str):
    r = Redis(R_HOST, R_PORT)
    r.hset(key, 'expire', int(time()))


def delete_key_from_redis(key: str):
    r = Redis(R_HOST, R_PORT)
    r.delete(key)
