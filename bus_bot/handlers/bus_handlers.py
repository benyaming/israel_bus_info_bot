import logging

import aiogram_metrics
from aiogram.types import Message, CallbackQuery

from bus_bot import texts
from bus_bot.clients.bus_api import prepare_station_schedule
from bus_bot.clients.map_generator import get_map_with_points
from bus_bot.helpers import get_cancel_button, CallbackPrefix
from bus_bot.misc import bot, watcher_manager


logger = logging.getLogger('bot')


async def on_stop_code(msg: Message):
    station_id = int(msg.text)

    content = await prepare_station_schedule(station_id)
    kb = get_cancel_button(msg.text)
    sent = await msg.reply(content, reply_markup=kb)
    aiogram_metrics.manual_track('Init station schedule')

    await watcher_manager.add_watch(msg.from_user.id, station_id, sent.message_id)


@aiogram_metrics.track('Terminate station tracking')
async def on_terminate_call(call: CallbackQuery):
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await call.answer(texts.stop_button)

    watcher_manager.remove_watch(call.message.message_id)


@aiogram_metrics.track('Location sent')
async def on_location(msg: Message):
    resp, kb = await get_map_with_points(msg.location.latitude, msg.location.longitude)
    await msg.reply_photo(resp, reply_markup=kb)


@aiogram_metrics.track('Stop from map selected')
async def on_stop_call(call: CallbackQuery):
    await call.answer()
    stop_code = int(call.data.split(CallbackPrefix.get_stop)[1])

    content = await prepare_station_schedule(stop_code)
    kb = get_cancel_button(stop_code)
    sent = await bot.send_message(call.from_user.id, content, reply_markup=kb)

    await watcher_manager.add_watch(call.from_user.id, stop_code, sent.message_id)
