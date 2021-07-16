import logging

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from aiogram.types import Message, ContentType
from aiogram.utils.executor import start_webhook, start_polling

import bus_bot.handlers
from bus_bot.misc import dp
from bus_bot.handlers.bot_lifecycle_hooks import on_start, on_shutdown
from bus_bot.config import (
    DOCKER_MODE,
    WEBAPP_PORT,
    WEBAPP_HOST,
    WEBHOOK_PATH,
    PERIOD,
    TTL,
    SENTRY_KEY
)
from bus_bot.core.map_generator.client import get_map_with_points
from bus_bot.sentry_middleware import SentryContextMiddleware

logger = logging.getLogger('bot')


ITERATIONS = TTL // PERIOD

if SENTRY_KEY:
    sentry_sdk.init(
        dsn=SENTRY_KEY,
        integrations=[AioHttpIntegration()]
    )
logger.info(f'Sentry is {"ENABLED" if SENTRY_KEY else "DISABLED"}')

dp.middleware.setup(SentryContextMiddleware())



#
# async def update_message(user_id: int, msg_id: int, station: int, *, is_last_update: bool = False):
#     content = await prepare_station_schedule(station, is_last_update)
#     kb = get_cancel_button(station) if not is_last_update else None
#
#     try:
#         await bot.edit_message_text(content, user_id, msg_id, reply_markup=kb)
#     except MessageNotModified:
#         pass
#
#
# async def updater(session: Session):
#     while True:
#         if session.next_station:
#             asyncio.create_task(
#                 update_message(
#                     session.user_id,
#                     session.msg_id,
#                     session.current_station,
#                     is_last_update=True
#                 )
#             )
#             session.reset()
#
#         await asyncio.sleep(PERIOD)
#
#         if session.updates_count > 0:
#             await update_message(session.user_id, session.msg_id, session.current_station)
#             session.updates_count -= 1
#         elif session.updates_count == 0:
#             await update_message(session.user_id, session.msg_id, session.current_station, is_last_update=True)
#             del SESSION_STORAGE[session.user_id]
#             break


# @dp.message_handler(lambda msg: msg.text.isdigit(), content_types=ContentTypes.TEXT)
# async def station_handler(msg: Message):
#     if msg.from_user.id in SESSION_STORAGE:
#         session = SESSION_STORAGE[msg.from_user.id]
#         is_next_station = True
#     else:
#         session = Session(msg.from_user.id, msg.text)
#         is_next_station = False
#
#     content = await prepare_station_schedule(station_id=msg.text)
#     kb = get_cancel_button(msg.text)
#     sent = await msg.reply(content, reply_markup=kb)
#     aiogram_metrics.manual_track('Init station schedule')
#
#     if not is_next_station:
#         session.msg_id = sent.message_id
#         asyncio.create_task(updater(session))
#     else:
#         session.next_station = msg.text
#         session.next_msg_id = sent.message_id


# @dp.message_handler()
# @aiogram_metrics.track('Unknown message')
# async def incorrect_message_handler(msg: Message):
#     await msg.reply(texts.incorrect_message)


# @dp.callback_query_handler(text_startswith=CallbackPrefix.stop_updates)
# @aiogram_metrics.track('Stop station tracking')
# async def handle_stop_query(call: CallbackQuery):
#     await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
#     await call.answer(texts.stop_button)
#
#     session = SESSION_STORAGE[call.from_user.id]
#     if session.current_station != call.data:
#         await asyncio.sleep(PERIOD)
#
#     session.updates_count = 0


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


@dp.message_handler(content_types=[ContentType.LOCATION, ContentType.VENUE])
async def handle_location(msg: Message):
    resp, kb = await get_map_with_points(msg.location.latitude, msg.location.longitude)
    await msg.reply_photo(resp, reply_markup=kb)


if __name__ == '__main__':
    if DOCKER_MODE:

        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
            skip_updates=True,
            on_startup=on_start,
            on_shutdown=on_shutdown
        )
    else:
        start_polling(dp, on_startup=on_start)


# TODO - REFACTOR IT!!!
