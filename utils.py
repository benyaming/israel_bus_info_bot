from time import time

import redis
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.apihelper import ApiException
from telebot import TeleBot
from redis import Redis
import requests

import settings
from bus_api import get_bus_info


def get_cancel_button(redis_key: str):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text='Stop updating',
            callback_data=redis_key
        )
    )
    return keyboard


def update_message(data: dict, last_message=False):
    bot = TeleBot(settings.TOKEN)
    bus_data = get_bus_info(data['station'])['data']
    response = bus_data if not last_message else \
        f'{bus_data}\n\n*Message not updating!*'

    keyboard = get_cancel_button(data['redis_key']) if not last_message \
        else None
    try:
        params = {
            'chat_id': data['user_id'],
            'message_id': data['message_id'],
            'parse_mode': 'Markdown',
            'reply_markup': keyboard.to_json()
        }
        url = f'https://api.telegram.org/bot{settings.TOKEN}/editmessagetext'
        requests.get(url, params)
    except ApiException as e:
        print(e.result)


def init_redis_tracking(user_id: int, station_id: int, message_id: int,
                        redis_key: str):
    r = redis.Redis(settings.r_host, settings.r_port)
    data = {
        'id': user_id,
        'station': station_id,
        'updated': int(time()),
        'message_id': message_id,
        'expire': int(time()) + int(settings.TTL)
    }
    r.hmset(redis_key, data)


def update_last_updated_ts(key: str):
    r = Redis(settings.r_host, settings.r_port)
    r.hset(key, 'last_send', int(time()))


def set_expired(key: str):
    r = Redis(settings.r_host, settings.r_port)
    r.hset(key, 'expire', int(time()))


def delete_key_from_redis(key: str):
    r = Redis(settings.r_host, settings.r_port)
    r.delete(key)
