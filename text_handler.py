# -*- coding: utf-8 -*-
from time import time

from telebot import TeleBot
from telebot.types import Message

import settings
import bus_api
from utils import get_cancel_button, init_redis_tracking


# todo user sent same station again


class TextHandler(object):

    def __init__(self, message: Message):
        self._user_id = message.from_user.id
        self._text = message.text
        self._message_id = message.message_id
        self._bot = TeleBot(settings.TOKEN)

    def verify_station_id(self) -> None:
        # todo check message before sending request
        if self._text.isdigit():
            station_id = int(self._text)
            self._get_station_info(station_id)
        else:
            self._send_error_message()

    def _get_station_info(self, station_id: int) -> None:
        response = bus_api.get_bus_info(int(station_id))
        if response['ok']:
            redis_key = f'users:{self._user_id}:{int(time())}'
            keyboard = get_cancel_button(redis_key)
            msg = self._bot.send_message(
                self._user_id, response['data'],
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            init_redis_tracking(self._user_id, station_id, msg.message_id,
                                redis_key)
        else:
            self._send_error_message(station=True)

    def _send_error_message(self, station=None) -> None:
        # todo error message
        if station:
            response = 'Wrong station number!'
            self._bot.send_message(self._user_id, response)
