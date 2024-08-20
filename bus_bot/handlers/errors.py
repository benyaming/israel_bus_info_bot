import logging

import sentry_sdk
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent, Message, CallbackQuery

from bus_bot import texts
from bus_bot.clients.bus_api.exceptions import BotError


logger = logging.getLogger(__file__)


async def on_err_not_modified(_, event: ErrorEvent):
    e: TelegramBadRequest = event.exception
    print('todo')
    print(e)


async def on_err_station_not_exists(_, message: Message):
    await message.reply(texts.invalid_station)


async def on_err_not_stations_found(_, message: Message):
    await message.reply(texts.no_stops_found)


async def on_err_api_not_responding(_, message: Message):
    await message.reply(texts.api_not_responding)


async def on_err_api_timeout(*_):
    # todo
    print('todo - on_err_api_timeout')


async def on_err_stop_already_saved(_, callback_query: CallbackQuery):
    await callback_query.answer(texts.stop_already_saved)


async def on_err_unknown_exception(event: ErrorEvent):
    if isinstance(event.exception, BotError):
        return

    if event.update.message:
        user = event.update.message.from_user
    elif event.update.callback_query:
        user = event.update.callback_query.from_user
    else:
        raise event.exception

    event.bot and await event.bot.send_message(user.id, texts.unknown_exception)
    logger.exception(event.exception)
    sentry_sdk.capture_exception(event.exception)
