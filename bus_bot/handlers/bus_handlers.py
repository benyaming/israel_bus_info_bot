import logging

import aiogram_metrics
from aiogram.types import ContentTypes, Message, ContentType, CallbackQuery

from bus_bot import texts
from bus_bot.core.bus_api_v3.client import prepare_station_schedule
from bus_bot.core.map_generator.client import get_map_with_points
from bus_bot.helpers import get_cancel_button, CallbackPrefix
from bus_bot.misc import dp, bot, update_service


logger = logging.getLogger('bot')


@dp.message_handler(lambda msg: msg.text.isdigit(), content_types=ContentTypes.TEXT)
async def station_handler(msg: Message):
    station_id = int(msg.text)

    content = await prepare_station_schedule(station_id)
    kb = get_cancel_button(msg.text)
    sent = await msg.reply(content, reply_markup=kb)
    aiogram_metrics.manual_track('Init station schedule')

    await update_service.add_watch(msg.from_user.id, station_id, sent.message_id)


@dp.callback_query_handler(text_startswith=CallbackPrefix.stop_updates)
@aiogram_metrics.track('Stop station tracking')
async def handle_stop_query(call: CallbackQuery):
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await call.answer(texts.stop_button)

    update_service.remove_watch(call.message.message_id)


# @dp.callback_query_handler(text_startswith=CallbackPrefix.get_stop)
# @aiogram_metrics.track('Stop from map selected')
# async def handle_station_selection(call: CallbackQuery):
#     await call.answer()
#     stop_code = int(call.data.split(CallbackPrefix.get_stop)[1])
#
#     if call.from_user.id in SESSION_STORAGE:
#         session = SESSION_STORAGE[call.from_user.id]
#         is_next_station = True
#     else:
#         session = Session(call.from_user.id, stop_code)
#         is_next_station = False
#
#     content = await prepare_station_schedule(station_id=stop_code)
#     kb = get_cancel_button(stop_code)
#     sent = await bot.send_message(call.from_user.id, content, reply_markup=kb)
#
#     if not is_next_station:
#         session.msg_id = sent.message_id
#         asyncio.create_task(updater(session))
#     else:
#         session.next_station = stop_code
#         session.next_msg_id = sent.message_id


# @dp.message_handler(content_types=[ContentType.LOCATION, ContentType.VENUE])
# async def handle_location(msg: Message):
#     resp, kb = await get_map_with_points(msg.location.latitude, msg.location.longitude)
#     await msg.reply_photo(resp, reply_markup=kb)
