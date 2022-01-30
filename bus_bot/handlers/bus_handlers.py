import logging

import aiogram.utils.exceptions
import aiogram_metrics
import aiohttp
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from bus_bot import texts
from bus_bot.clients.bus_api import prepare_station_schedule
from bus_bot.clients.bus_api.client import get_stop_info
from bus_bot.clients.map_generator import get_map_with_points
from bus_bot.exceptions import StopAlreadySaved
from bus_bot.helpers import CallbackPrefix, chat_action
from bus_bot.keyboards import get_kb_for_stop, get_done_button_with_placeholder
from bus_bot.misc import bot, dp
from bus_bot.repository import user_repository
from bus_bot.states import RenameStopState
from bus_bot.config import env

logger = logging.getLogger('bot')


@chat_action
async def on_stop_code(msg: Message):
    stop_code = int(msg.text)
    user = await user_repository.get_user(msg.from_user.id)

    content, kb = await prepare_station_schedule(stop_code)

    # kb = get_kb_for_stop(msg.text, is_saved=user.is_stop_already_saved(stop_code))
    sent = await msg.reply(content, reply_markup=kb)
    aiogram_metrics.manual_track('Init station schedule')

    await dp['watcher_manager'].add_watch(msg.from_user.id, stop_code, sent.message_id)


@aiogram_metrics.track('Terminate station tracking')
async def on_terminate_call(call: CallbackQuery):
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await call.answer(texts.cancel_updating_alert)

    dp['watcher_manager'].remove_watch(call.message.message_id)


@aiogram_metrics.track('Location sent')
@chat_action('image')
async def on_location(msg: Message):
    resp, kb = await get_map_with_points(msg.location.latitude, msg.location.longitude)
    await msg.reply_photo(resp, reply_markup=kb)


@chat_action
async def on_stop_call(call: CallbackQuery):
    prefix, raw_stop_code = call.data.split('_', maxsplit=1)
    stop_code = int(raw_stop_code)

    if prefix == CallbackPrefix.get_stop[:-1]:
        aiogram_metrics.manual_track('Stop from map selected')
    elif prefix == CallbackPrefix.get_saved_stop[:-1]:
        aiogram_metrics.manual_track('Stop from saved stops selected')

    user = await user_repository.get_user(call.from_user.id)

    content, kb = await prepare_station_schedule(stop_code)
    # kb = get_kb_for_stop(stop_code, is_saved=user.is_stop_already_saved(stop_code))
    sent = await bot.send_message(call.from_user.id, content, reply_markup=kb)
    await call.answer()

    await dp['watcher_manager'].add_watch(call.from_user.id, stop_code, sent.message_id)


async def on_track_call(call: CallbackQuery):
    await call.answer()
    stop_code, plate_number = call.data.split(CallbackPrefix.track_route)[1].split(':')

    loc_msg = None
    async with bot.session.ws_connect(f'{env.API_URL}/track_vehicle/{stop_code}/{plate_number}') as ws:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.json()
                print(data)
                lat = data['latitude']
                lng = data['longitude']
                if loc_msg is None:
                    loc_msg = await bot.send_location(call.from_user.id, lat, lng, live_period=1800)
                else:
                    try:
                        await bot.edit_message_live_location(lat, lng, call.from_user.id, loc_msg.message_id)
                    except aiogram.utils.exceptions.MessageNotModified:
                        continue

@aiogram_metrics.track('Save stop')
async def on_save_stop(call: CallbackQuery, state: FSMContext):
    stop_code = int(call.data.split(CallbackPrefix.save_stop)[1])

    user = await user_repository.get_user(call.from_user.id)
    if user.is_stop_already_saved(stop_code):
        raise StopAlreadySaved()

    stop_details = await get_stop_info(stop_code)

    data = {'stop_rename': {'code': stop_code, 'name': stop_details.name, 'origin': call.message.message_id}}
    await state.set_data(data)

    kb = get_done_button_with_placeholder(stop_details.name)
    await bot.send_message(call.from_user.id, texts.rename_saved_stop, reply_markup=kb)
    await call.answer()
    await RenameStopState.waiting_for_stop_name.set()


@aiogram_metrics.track('Delete stop')
async def on_remove_stop(call: CallbackQuery):
    stop_code = int(call.data.split(CallbackPrefix.remove_stop)[1])
    await user_repository.remove_stop(call.from_user.id, stop_code)
    kb = get_kb_for_stop(stop_code, False)
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=kb)
    await call.answer(texts.stop_deleted_ok_alert)

