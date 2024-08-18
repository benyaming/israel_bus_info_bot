import logging

import aiogram_metrics
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile, ContentType
from httpx import AsyncClient

from bus_bot import texts
from bus_bot.clients.bus_api import prepare_station_schedule
from bus_bot.clients.bus_api.client import get_stop_info
from bus_bot.clients.map_generator import get_map_with_points
from bus_bot.exceptions import StopAlreadySaved
from bus_bot.helpers import CallbackPrefix
from bus_bot.keyboards import get_kb_for_stop, get_done_button_with_placeholder
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

    content = await prepare_station_schedule(stop_code, http_session)

    kb = get_kb_for_stop(stop_code, is_saved=user.is_stop_already_saved(stop_code))
    sent = await message.reply(content, reply_markup=kb)
    aiogram_metrics.manual_track('Init station schedule')

    await watcher_manager.add_watch(message.from_user, stop_code, sent.message_id, message.bot, db_repo, http_session)


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
    resp, kb = await get_map_with_points(message.location.latitude, message.location.longitude, http_session)
    await message.reply_photo(photo=BufferedInputFile(file=resp.read(), filename=''), reply_markup=kb)


async def on_stop_call(
        callback_query: CallbackQuery,
        db_repo: DbRepo,
        watcher_manager: WatcherManager,
        http_session: AsyncClient
):
    prefix, raw_stop_code = callback_query.data.split('_', maxsplit=1)
    stop_code = int(raw_stop_code)

    if prefix == CallbackPrefix.get_stop[:-1]:
        aiogram_metrics.manual_track('Stop from map selected')
    elif prefix == CallbackPrefix.get_saved_stop[:-1]:
        aiogram_metrics.manual_track('Stop from saved stops selected')

    user = await db_repo.get_user(callback_query.from_user)

    content = await prepare_station_schedule(stop_code, http_session)
    kb = get_kb_for_stop(stop_code, is_saved=user.is_stop_already_saved(stop_code))
    sent = await callback_query.bot.send_message(callback_query.from_user.id, content, reply_markup=kb)
    await callback_query.answer()

    await watcher_manager.add_watch(callback_query.from_user, stop_code, sent.message_id, callback_query.bot, db_repo, http_session)


@aiogram_metrics.track('Save stop')
async def on_save_stop(
        callback_query: CallbackQuery,
        state: FSMContext,
        db_repo: DbRepo,
        http_session: AsyncClient
):
    stop_code = int(callback_query.data.split(CallbackPrefix.save_stop)[1])

    user = await db_repo.get_user(callback_query.from_user)
    if user.is_stop_already_saved(stop_code):
        raise StopAlreadySaved()

    stop_details = await get_stop_info(stop_code, http_session)

    data = {'stop_rename': {'code': stop_code, 'name': stop_details.name, 'origin': callback_query.message.message_id}}
    await state.set_data(data)

    kb = get_done_button_with_placeholder(stop_details.name)
    await callback_query.bot.send_message(callback_query.from_user.id, texts.rename_saved_stop, reply_markup=kb)
    await callback_query.answer()
    await RenameStopState.waiting_for_stop_name.set()


@aiogram_metrics.track('Delete stop')
async def on_remove_stop(
        callback_query: CallbackQuery,
        db_repo: DbRepo,
):
    stop_code = int(callback_query.data.split(CallbackPrefix.remove_stop)[1])
    await db_repo.remove_stop(callback_query.from_user, stop_code)
    kb = get_kb_for_stop(stop_code, False)
    await callback_query.bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=kb
    )
    await callback_query.answer(texts.stop_deleted_ok_alert)


router = Router()
router.message.register(on_stop_code, F.text.isdigit() & F.content_type == ContentType.TEXT)
router.message.register(on_location, F.content_type.in_({ContentType.LOCATION, ContentType.VENUE}))
router.callback_query.register(on_terminate_call, F.text.startswith(CallbackPrefix.terminate_stop_updating))
router.callback_query.register(
    on_stop_call,
    F.data.startswith(CallbackPrefix.get_stop) | F.data.startswith(CallbackPrefix.get_saved_stop)
)
router.callback_query.register(on_save_stop, F.data.startswith(CallbackPrefix.save_stop))
router.callback_query.register(on_remove_stop, F.data.startswith(CallbackPrefix.remove_stop))
