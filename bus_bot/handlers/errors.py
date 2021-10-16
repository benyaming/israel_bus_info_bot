import logging

import sentry_sdk
from aiogram.types import Message, User, CallbackQuery

from bus_bot import texts
from bus_bot.clients.bus_api.exceptions import BotError
from bus_bot.misc import bot


logger = logging.getLogger(__file__)


async def on_err_not_modified(*_):
    return True


async def on_err_station_not_exists(*_):
    msg = Message.get_current()
    await msg.reply(texts.invalid_station)
    return True


async def on_err_not_stations_found(*_):
    msg = Message.get_current()
    await msg.reply(texts.no_stops_found)
    return True


async def on_err_api_not_responding(*_):
    msg = Message.get_current()
    await msg.reply(texts.api_not_responding)
    return True


async def on_err_api_timeout(*_):
    return True


async def on_err_stop_already_saved(*_):
    call = CallbackQuery.get_current()
    await call.answer(texts.stop_already_saved)
    return True


async def on_err_unknown_exception(_, e: Exception):
    if isinstance(e, BotError):
        return True

    await bot.send_message(User.get_current().id, texts.unknown_exception)
    logger.exception(e)
    sentry_sdk.capture_exception(e)
    return True
