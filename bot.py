# -*- coding: utf-8 -*-
from time import sleep

import telebot
from flask import Flask, request

import settings
import text_handler
from utils import set_expired

route_path = f'/{settings.URI}/'

bot = telebot.TeleBot(settings.TOKEN)

app = Flask(__name__)


@app.route(route_path, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok'


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.from_user.id,
        'Welcome! Input station ID'
    )


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message: telebot.types.Message):
    bot.send_chat_action(message.from_user.id, 'typing')
    text_handler.TextHandler(message).verify_station_id()


@bot.callback_query_handler(func=lambda call: True)
def handle_call(call: telebot.types.CallbackQuery):
    bot.answer_callback_query(call.id)
    set_expired(call.data)


if __name__ == '__main__':
    if not settings.IS_SERVER:
        bot.remove_webhook()
        sleep(1)
        bot.polling(True, timeout=50)
