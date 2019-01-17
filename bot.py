import asyncio
import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.utils.executor import start_polling

from text_handler import handle_text
from utils import init_redis_track, stop_redis_track, get_cancel_button
from settings import TOKEN, IS_SERVER, WEBAPP_PORT, WEBAPP_HOST, WEBHOOK_PATH


logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=TOKEN, loop=loop)
dp = Dispatcher(bot)


# Handler for all text messages
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


# Handler for "Stop tracking" Callback button
@dp.callback_query_handler(lambda callback_query: True)
async def habdle_stop_query(call: types.CallbackQuery):
    await call.answer('Will stop soon')  # TODO normal text
    await stop_redis_track(call.from_user.id, loop=dp.loop)


if __name__ == '__main__':
    if IS_SERVER:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            loop=loop,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT
        )
    else:
        start_polling(dp)
