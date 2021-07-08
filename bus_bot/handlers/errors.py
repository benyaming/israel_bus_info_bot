import logging

import sentry_sdk
from aiogram.types import Message, User
from aiogram.utils.exceptions import MessageNotModified

from bus_bot import texts
from bus_bot.core.bus_api_v3.exceptions import StationNonExistsException, ApiNotRespondingException, BotException
from bus_bot.misc import dp, bot


logger = logging.getLogger(__file__)


@dp.errors_handler(exception=MessageNotModified)
async def handle_not_modified(*_):
    return True


@dp.errors_handler(exception=StationNonExistsException)
async def handle_station_not_exists(*_):
    msg = Message.get_current()
    await msg.reply(texts.invalid_station)
    return True


@dp.errors_handler(exception=ApiNotRespondingException)
async def handle_station_not_exists(*_):
    msg = Message.get_current()
    await msg.reply(texts.api_not_responding)
    return True


@dp.errors_handler(exception=Exception)
async def handle_unknown_exception(_, e: Exception):
    if isinstance(e, BotException):
        return True

    await bot.send_message(User.get_current().id, texts.unknown_exception)
    logger.exception(e)
    sentry_sdk.capture_exception(e)
    return True
