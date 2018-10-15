# -*- coding: utf-8 -*-
import settings
import bus_api

from telebot import TeleBot


def verify_station_id(station_id: str) -> None:
    if station_id.isdigit():
        station_id = int(station_id)
        get_station_info(station_id)
    else:
        send_error_message()


def get_station_info(station_id) -> None:
    response = bus_api.get_bus_info(station_id)
    bot.send_message(user, response, parse_mode='Markdown')


def send_error_message() -> None:
    pass


def handle_text(user_id: int, text: str) -> None:
    global bot, user
    bot = TeleBot(settings.TOKEN)
    user = user_id
    verify_station_id(text)
