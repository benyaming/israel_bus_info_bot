import aiogram_metrics
from aiogram.types import Message

from bus_bot import texts
from bus_bot.helpers import check_user
from bus_bot.misc import dp, bot


@dp.message_handler(commands=['start'])
@aiogram_metrics.track('/start command')
async def handle_start(message: Message):
    await bot.send_message(message.chat.id, texts.start_command)
    await check_user()


@dp.message_handler(commands=['help'])
@aiogram_metrics.track('/help command')
async def handle_help(message: Message):
    await bot.send_message(message.chat.id, texts.help_command)
