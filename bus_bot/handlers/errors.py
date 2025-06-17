import logging

import sentry_sdk
from aiogram.types import ErrorEvent, Message, CallbackQuery, Update

from bus_bot import texts
from bus_bot.clients.bus_api.exceptions import BotError


logger = logging.getLogger(__file__)


async def on_err_not_modified(event: ErrorEvent, update: Update):
    print('todo')
    print(event)


async def on_err_station_not_exists(event: ErrorEvent):
    if event.update.message:
        await event.update.message.reply(texts.invalid_station)
    elif event.update.callback_query:
        await event.update.callback_query.answer(texts.invalid_station, show_alert=True)


async def on_err_not_stations_found(event: ErrorEvent):
    if event.update.message:
        await event.update.message.reply(texts.no_stops_found)
    elif event.update.callback_query:
        await event.update.callback_query.answer(texts.no_stops_found, show_alert=True)


async def on_err_api_not_responding(event: ErrorEvent):
    if event.update.message:
        await event.update.message.reply(texts.api_not_responding)
    elif event.update.callback_query:
        await event.update.callback_query.answer(texts.api_not_responding, show_alert=True)


async def on_err_api_timeout(event: ErrorEvent):
    print('todo - on_err_api_timeout')
    if event.update.message:
        await event.update.message.reply(texts.api_not_responding)
    elif event.update.callback_query:
        await event.update.callback_query.answer(texts.api_not_responding, show_alert=True)


async def on_err_stop_already_saved(event: ErrorEvent, update: Update):
    if update.message:
        await update.message.reply(texts.stop_already_saved)
    elif update.callback_query:
        await event.update.callback_query.answer(texts.stop_already_saved)


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
