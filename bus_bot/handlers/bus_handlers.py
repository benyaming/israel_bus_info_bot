import logging

import aiogram_metrics
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile, ContentType
from httpx import AsyncClient

from bus_bot import texts
from bus_bot.clients.bus_api import prepare_stop_schedule
from bus_bot.clients.bus_api.exceptions import NoStopsError
from bus_bot.clients.bus_api.client import get_stop_by_code, get_stop_by_id, find_near_stops, get_stop_by_parent_id
from bus_bot.clients.map_generator import get_map_with_points
from bus_bot.exceptions import StopAlreadySaved
from bus_bot.helpers import CallbackPrefix
from bus_bot.keyboards import get_kb_for_stop, get_done_button_with_placeholder, get_kb_for_stops_map
from bus_bot.repository.user_repository import DbRepo
from bus_bot.states import RenameStopState
from bus_bot.service.watcher_management_service import WatcherManager

logger = logging.getLogger('bot')


async def on_stop_code(
    message: Message,
    db_repo: DbRepo,
    http_session: AsyncClient,
    watcher_manager: WatcherManager
):
    await message.bot.send_chat_action(message.chat.id, 'typing')

    stop_code = int(message.text)
    user = await db_repo.get_user(message.from_user)

    stop = await get_stop_by_code(stop_code, http_session)
    content = await prepare_stop_schedule(stop.id, http_session)

    kb = get_kb_for_stop(stop.id, is_saved=user.is_stop_already_saved(stop.id))
    sent = await message.reply(content, reply_markup=kb)
    aiogram_metrics.manual_track('Init station schedule', message=message)

    await watcher_manager.add_watch(message.from_user, stop.id, sent.message_id, message.bot, db_repo, http_session)


@aiogram_metrics.track('Terminate station tracking')
async def on_terminate_call(callback_query: CallbackQuery, watcher_manager: WatcherManager):
    await callback_query.bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id
    )
    await callback_query.answer(texts.cancel_updating_alert)

    watcher_manager.remove_watch(callback_query.message.message_id)


@aiogram_metrics.track('Location sent')
async def on_location(message: Message, http_session: AsyncClient):
    await message.bot.send_chat_action(message.chat.id, 'upload_photo')
    
    stops = await find_near_stops(message.location.latitude, message.location.longitude, http_session)
    if len(stops) == 0:
        raise NoStopsError
    
    resp = await get_map_with_points(stops, http_session)
    kb = get_kb_for_stops_map(stops)
    await message.reply_photo(photo=BufferedInputFile(file=resp.read(), filename=''), reply_markup=kb)


async def on_stop_call(
    callback_query: CallbackQuery,
    db_repo: DbRepo,
    watcher_manager: WatcherManager,
    http_session: AsyncClient
):
    prefix, raw_stop_id = callback_query.data.split('_', maxsplit=1)
    stop_id = int(raw_stop_id)

    if prefix == CallbackPrefix.get_stop[:-1]:
        aiogram_metrics.manual_track('Stop from map selected', callback_query=callback_query)
    elif prefix == CallbackPrefix.get_saved_stop[:-1]:
        aiogram_metrics.manual_track('Stop from saved stops selected', callback_query=callback_query)

    user = await db_repo.get_user(callback_query.from_user)

    content = await prepare_stop_schedule(stop_id, http_session)
    kb = get_kb_for_stop(stop_id, is_saved=user.is_stop_already_saved(stop_id))
    sent = await callback_query.bot.send_message(callback_query.from_user.id, content, reply_markup=kb)
    await callback_query.answer()

    await watcher_manager.add_watch(callback_query.from_user, stop_id, sent.message_id, callback_query.bot, db_repo, http_session)


@aiogram_metrics.track('Restart stop updating')
async def on_restart_stop_update_call(
    callback_query: CallbackQuery,
    watcher_manager: WatcherManager,
    db_repo: DbRepo,
    http_session: AsyncClient
):
    stop_id = int(callback_query.data.split(CallbackPrefix.restart_stop_updating)[1])
    user = await db_repo.get_user(callback_query.from_user)

    content = await prepare_stop_schedule(stop_id, http_session)
    kb = get_kb_for_stop(stop_id, is_saved=user.is_stop_already_saved(stop_id))
    
    sent = await callback_query.bot.edit_message_text(
        content, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, reply_markup=kb
    )
    
    await watcher_manager.add_watch(callback_query.from_user, stop_id, sent.message_id, callback_query.bot, db_repo, http_session)


@aiogram_metrics.track('Save stop')
async def on_save_stop(
    callback_query: CallbackQuery,
    state: FSMContext,
    db_repo: DbRepo,
    http_session: AsyncClient
):
    stop_id = int(callback_query.data.split(CallbackPrefix.save_stop)[1])

    user = await db_repo.get_user(callback_query.from_user)
    if user.is_stop_already_saved(stop_id):
        raise StopAlreadySaved()

    stop_details = await get_stop_by_id(stop_id, http_session)

    data = {'stop_rename': {'id': stop_id, 'name': stop_details.name, 'origin': callback_query.message.message_id}}
    await state.set_data(data)

    kb = get_done_button_with_placeholder(stop_details.name)
    await callback_query.bot.send_message(callback_query.from_user.id, texts.rename_saved_stop, reply_markup=kb)
    await callback_query.answer()
    await state.set_state(RenameStopState.waiting_for_stop_name)


@aiogram_metrics.track('Delete stop')
async def on_remove_stop(callback_query: CallbackQuery, db_repo: DbRepo):
    stop_id = int(callback_query.data.split(CallbackPrefix.remove_stop)[1])
    await db_repo.remove_stop(callback_query.from_user, stop_id)
    kb = get_kb_for_stop(stop_id, False)
    await callback_query.bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=kb
    )
    await callback_query.answer(texts.stop_deleted_ok_alert)
    
    
# @aiogram_metrics.track('Platform menu entered')
# async def on_platform_menu(callback_query: CallbackQuery, http_session: AsyncClient):
#     parent_stop_id = int(callback_query.data.split('_')[1])
#     stops = await get_stop_by_parent_id(parent_stop_id, http_session)
#     kb = get_platforms_kb(stops)
#     await callback_query.bot.edit_message_reply_markup(
#         chat_id=callback_query.from_user.id,
#         message_id=callback_query.message.message_id,
#         reply_markup=kb
#     )


router = Router()
router.message.register(on_stop_code, F.text.isdigit() & F.content_type == ContentType.TEXT)
router.message.register(on_location, F.content_type.in_({ContentType.LOCATION, ContentType.VENUE}))
router.callback_query.register(on_terminate_call, F.data.startswith(CallbackPrefix.terminate_stop_updating))
router.callback_query.register(
    on_stop_call,
    F.data.startswith(CallbackPrefix.get_stop) | F.data.startswith(CallbackPrefix.get_saved_stop)
)
router.callback_query.register(on_save_stop, F.data.startswith(CallbackPrefix.save_stop))
router.callback_query.register(on_remove_stop, F.data.startswith(CallbackPrefix.remove_stop))
router.callback_query.register(on_restart_stop_update_call, F.data.startswith(CallbackPrefix.restart_stop_updating))
# router.callback_query.register(on_platform_menu, F.data.startswith(CallbackPrefix.get_platform_menu))
