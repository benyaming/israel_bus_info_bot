import asyncio
import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.utils.executor import start_polling

from text_handler import handle_text
from utils import init_redis_track, get_cancel_button
from settings import TOKEN, IS_SERVER, WEBAPP_PORT, WEBAPP_HOST


logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=TOKEN, loop=loop)
dp = Dispatcher(bot)


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def qwe(message: types.message):
    response = await handle_text(message.text)
    if response['ok']:
        keyboard = get_cancel_button()
        msg = await bot.send_message(
            message.chat.id, response['data'],
            parse_mode='Markdown',
            reply_markup=keyboard)
        await init_redis_track(
            user_id=message.chat.id,
            message_id=msg.message_id,
            station_id=message.text,
            loop=dp.loop)
    else:
        await bot.send_message(message.chat.id, response['data'])


if __name__ == '__main__':
    if IS_SERVER:
        start_webhook(
            dispatcher=dp,
            webhook_path=None,
            loop=loop,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT
        )
    else:
        start_polling(dp)
