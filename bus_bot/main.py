import asyncio
from dataclasses import dataclass
from typing import Optional

import aiopg
from aiogram.types import ContentTypes, Message, CallbackQuery, Update
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook, start_polling
from aiogram.utils.exceptions import MessageNotModified

from bus_bot.text_handler import handle_text
from bus_bot.helpers import get_cancel_button, check_user, UserData
from bus_bot.bus_api import get_lines, is_station_valid
from bus_bot.config import IS_SERVER, WEBAPP_PORT, WEBAPP_HOST, WEBHOOK_PATH, PERIOD, TTL, DSN
from bus_bot.misc import bot, dp, logger
from bus_bot.sessions import Session, SESSION_STORAGE


ITERATIONS = TTL // PERIOD


async def on_start(dispatcher: Dispatcher):
    logger.info('STARTING BUS BOT...')
    # db_conn = await aiopg.create_pool(dsn=DSN)
    # dispatcher['db_pool'] = db_conn


# async def update_message(user_id: int, last: bool = False) -> None:
#     user_data: UserData = await dp.storage.get_data(user=user_id)
#     text = await get_lines(user_data.station_id, last=last)
#     kb = get_cancel_button() if not last else None
#     await bot.edit_message_text(
#         text,
#         user_data.user_id,
#         user_data.message_id,
#         reply_markup=kb
#     )
#
#
# # TODO TEST IT
# async def schedule_next_station(user_id: int, message_id: int, station_id: int) -> ...:
#     """
#     Scheduler for new stations. If user already subscribed for station, updates it's
#     data. Runs updater, if it need.
#     """
#     user_data: UserData = await dp.storage.get_data(user=user_id)
#     if not user_data:
#         data = UserData(user_id=user_id, station_id=station_id, message_id=message_id)
#         await dp.storage.set_data(user=user_id, data=data)
#         await run_updater(user_id)
#     else:
#         user_data.next_station_id = station_id
#         user_data.next_message_id = message_id
#         await dp.storage.set_data(user=user_id, data=user_data)
#
#
# async def run_updater(user_id: int) -> None:
#     """
#     Warning! Do NOT delete `station_id` from `user_data`.
#     If you want to stop updater, set `user_data.stop_updating` to `True`.
#     """
#     for n in range(ITERATIONS):
#         await asyncio.sleep(PERIOD)
#         user_data: UserData = await dp.storage.get_data(user=user_id)
#
#         if not user_data.next_station_id and not user_data.stop_updating:
#             try:
#                 await update_message(user_id)
#             except MessageNotModified:
#                 # If lines list not changing during iteration, just skip this iteration
#                 continue
#         else:
#             break
#
#     user_data: UserData = await dp.storage.get_data(user=user_id)
#     if user_data.next_station_id:
#         await update_message(user_id, last=True)
#         user_data.station_id = user_data.next_station_id
#         user_data.message_id = user_data.next_message_id
#         user_data.next_station_id = None
#         user_data.next_message_id = None
#         await dp.storage.set_data(user=user_id, data=user_data)
#         return await run_updater(user_data.user_id)
#
#     await update_message(user_id, last=True)
#     await dp.storage.reset_data(user=user_id)

@dp.errors_handler(exception=MessageNotModified)
async def not_modified(update: Update, e: MessageNotModified):
    print(repr(e))
    return True


# /start command handler
@dp.message_handler(commands=['start'])
async def handle_start(message: Message):
    response = 'Hi! Send me a station number!'
    await bot.send_message(message.chat.id, response)


# # /help command handler
# @dp.message_handler(commands=['help'])
# async def handle_help(message: Message):
#     response = 'Send to the bot station\'s number, and bot will send you ' \
#                'arrival times of nearest buses. The message with times will ' \
#                'updating each 15 seconds for 15 minutes or until you send ' \
#                'another number or will press "Stop tracking" button.\n\n' \
#                'Author: @benyomin\n' \
#                'Code: https://github.com/benyomin94/israel\\_bus\\_info\\_bot'
#     await bot.send_message(message.chat.id, response)
#
#
# # Handler for all text messages
# @dp.message_handler(content_types=ContentTypes.TEXT)
# async def text_handler(message: Message):
#     response = await handle_text(message.text)
#     keyboard = get_cancel_button() if response['ok'] else None
#     msg = await bot.send_message(message.chat.id, response['data'], reply_markup=keyboard)
#
#     if response['ok']:
#         # TODO test it!
#         await schedule_next_station(
#             message.from_user.id,
#             msg.message_id,
#             response['station_id']
#         )
#     await check_user()


async def update_message_v2(user_id: int, msg_id: int, station: int, *, last: bool = False):
    content = await get_lines(station, last)
    kb = get_cancel_button(station) if not last else None

    try:
        await bot.edit_message_text(content, user_id, msg_id, reply_markup=kb)
    except MessageNotModified:
        pass


async def updater(session: Session):
    while True:
        # print('iter')
        if session.next_station:
            asyncio.create_task(update_message_v2(session.user_id, session.msg_id, session.current_station, last=True))
            session.reset()

        await asyncio.sleep(PERIOD)

        if session.updates_count > 0:
            # print('Regular update, ', session.current_station)
            await update_message_v2(session.user_id, session.msg_id, session.current_station)
            session.updates_count -= 1
        elif session.updates_count == 0:
            # print('last update, ', session.current_station)
            await update_message_v2(session.user_id, session.msg_id, session.current_station, last=True)
            del SESSION_STORAGE[session.user_id]
            break


@dp.message_handler(lambda msg: msg.text.isdigit(), content_types=ContentTypes.TEXT)
async def station_handler(msg: Message):
    station_valid = await is_station_valid(msg.text)
    if not station_valid:
        ...

    if msg.from_user.id in SESSION_STORAGE:
        session = SESSION_STORAGE[msg.from_user.id]
        is_next_station = True
    else:
        session = Session(msg.from_user.id, msg.text)
        is_next_station = False

    content = await get_lines(station_id=msg.text)
    kb = get_cancel_button(msg.text)
    sent = await msg.reply(content, reply_markup=kb)

    if not is_next_station:
        session.msg_id = sent.message_id
        asyncio.create_task(updater(session))
    else:
        session.next_station = msg.text
        session.next_msg_id = sent.message_id


@dp.message_handler()
async def incorrect_message_handler(msg: Message):
    await msg.reply('Incorrect message! Please, send station number!')


# Handler for "Stop tracking" Callback button
@dp.callback_query_handler(lambda callback_query: True)
async def handle_stop_query(call: CallbackQuery):
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await call.answer('Will stop soon')  # TODO normal text

    session = SESSION_STORAGE[call.from_user.id]
    if session.current_station != call.data:
        await asyncio.sleep(PERIOD)

    session.updates_count = 0
    # user_data: UserData = await dp.storage.get_data(user=call.from_user.id)
    # user_data.stop_updating = True
    # await dp.storage.set_data(user=call.from_user.id, data=user_data)


if __name__ == '__main__':
    if IS_SERVER:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
            skip_updates=True,
            on_startup=on_start
        )
    else:
        start_polling(dp, on_startup=on_start)
