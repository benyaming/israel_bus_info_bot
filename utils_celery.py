from json import dumps
from time import time
from typing import Optional
from logging import info

from requests import get
from redis import Redis

from bus_api_celery import get_lines
from settings import TOKEN, R_HOST, R_PORT


def update(data: dict, last_message: Optional[bool] = None) -> None:
    """
    Simple sync function that updates text of message via requests
    :param data: dict with such data as user id, station number, message id
    :param last_message: if True appends "Not updating" string in text's end
    :return:
    """
    bus_data = get_lines(data['station'])

    response = bus_data if not last_message else \
        f'{bus_data}\n\n*Message not updating!*'

    params = {
        'chat_id': data['id'],
        'message_id': data['message_id'],
        'parse_mode': 'Markdown',
        'text': response
    }
    # generating simple inline keyboard if message still updating
    keyboard = dumps(
        {
            "inline_keyboard": [
                [{"text": "Stop updating", "callback_data": "::"}]]
        }
    ) if not last_message else None
    if keyboard:
        params['reply_markup'] = keyboard
    info('SENDING REQUEST TO TELEGRAM API...')

    url = f'https://api.telegram.org/bot{TOKEN}/editmessagetext'
    r = get(url, params)
    info(r.status_code)


def update_last_updated_ts(key: str) -> None:
    """
    Sync function that updates 'updated' value in redis hash
    :param key: redis key
    :return:
    """
    r = Redis(R_HOST, R_PORT)
    r.hset(key, 'updated', int(time()))


def set_expired(key: str):
    """
    Sync function that sets 'expire' value in hash equals to current timestamp
    :param key: redis key
    :return:
    """
    r = Redis(R_HOST, R_PORT)
    r.hset(key, 'expire', int(time()))


def delete_key_from_redis(key: str) -> None:
    """
    Sync function that deletes key from redis
    :param key: redis key
    :return:
    """
    r = Redis(R_HOST, R_PORT)
    r.delete(key)
