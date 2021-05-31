import asyncio

import aiopg
import aiogram_metrics
from aiogram.types import ContentTypes, Message, CallbackQuery, Update
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook, start_polling
from aiogram.utils.exceptions import MessageNotModified

from bus_bot.helpers import get_cancel_button, check_user
from bus_bot.bus_api import get_lines, is_station_valid
from bus_bot.config import (
    DOCKER_MODE,
    WEBAPP_PORT,
    WEBAPP_HOST,
    WEBHOOK_PATH,
    PERIOD,
    TTL,
    DSN,
    WEBHOOK_URL,
    METRICS_DSN,
    METRICS_TABLE_NAME
)
from bus_bot.misc import bot, dp, logger
from bus_bot.sessions import Session, SESSION_STORAGE
from bus_bot import texts

ITERATIONS = TTL // PERIOD


async def on_start(dispatcher: Dispatcher):
    logger.info('STARTING BUS BOT...')
    if DOCKER_MODE:
        await bot.set_webhook(WEBHOOK_URL)
    # db_conn = await aiopg.create_pool(dsn=DSN)
    # dispatcher['db_pool'] = db_conn

    await aiogram_metrics.register(METRICS_DSN, METRICS_TABLE_NAME)


async def on_shutdown(dispatcher: Dispatcher):
    logger.info('SHUTTING DOWN...')
    await aiogram_metrics.close()


@dp.errors_handler(exception=MessageNotModified)
async def not_modified(update: Update, e: MessageNotModified):
    logger.error(repr(e))
    return True


@dp.message_handler(commands=['start'])
@aiogram_metrics.track('/start command')
async def handle_start(message: Message):
    await bot.send_message(message.chat.id, texts.start_command)
    await check_user()


@dp.message_handler(commands=['help'])
@aiogram_metrics.track('/help command')
async def handle_help(message: Message):
    await bot.send_message(message.chat.id, texts.help_command)


async def update_message(user_id: int, msg_id: int, station: int, *, last: bool = False):
    content = await get_lines(station, last)
    kb = get_cancel_button(station) if not last else None

    try:
        await bot.edit_message_text(content, user_id, msg_id, reply_markup=kb)
    except MessageNotModified:
        pass


async def updater(session: Session):
    while True:
        if session.next_station:
            asyncio.create_task(update_message(session.user_id, session.msg_id, session.current_station, last=True))
            session.reset()

        await asyncio.sleep(PERIOD)

        if session.updates_count > 0:
            await update_message(session.user_id, session.msg_id, session.current_station)
            session.updates_count -= 1
        elif session.updates_count == 0:
            await update_message(session.user_id, session.msg_id, session.current_station, last=True)
            del SESSION_STORAGE[session.user_id]
            break


@dp.message_handler(lambda msg: msg.text.isdigit(), content_types=ContentTypes.TEXT)
async def station_handler(msg: Message):
    station_valid = await is_station_valid(msg.text)
    if not station_valid:
        aiogram_metrics.manual_track('Invalid station')
        return await msg.reply(texts.invalid_station)

    if msg.from_user.id in SESSION_STORAGE:
        session = SESSION_STORAGE[msg.from_user.id]
        is_next_station = True
    else:
        session = Session(msg.from_user.id, msg.text)
        is_next_station = False

    content = await get_lines(station_id=msg.text)
    kb = get_cancel_button(msg.text)
    sent = await msg.reply(content, reply_markup=kb)
    aiogram_metrics.manual_track('Init station schedule')

    if not is_next_station:
        session.msg_id = sent.message_id
        asyncio.create_task(updater(session))
    else:
        session.next_station = msg.text
        session.next_msg_id = sent.message_id


@dp.message_handler()
@aiogram_metrics.track('Unknown message')
async def incorrect_message_handler(msg: Message):
    await msg.reply(texts.incorrect_message)


@dp.callback_query_handler(lambda callback_query: True)
@aiogram_metrics.track('Stop station tracking')
async def handle_stop_query(call: CallbackQuery):
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
    await call.answer(texts.stop_button)

    session = SESSION_STORAGE[call.from_user.id]
    if session.current_station != call.data:
        await asyncio.sleep(PERIOD)

    session.updates_count = 0


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
