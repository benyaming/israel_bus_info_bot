import aiogram_metrics
from aiogram.types import Message, BotCommand

from bus_bot import texts
from bus_bot.misc import bot


@aiogram_metrics.track('/start command')
async def on_start_command(message: Message):
    await bot.send_message(message.chat.id, texts.start_command)
    # await check_user()


@aiogram_metrics.track('/help command')
async def on_help_command(message: Message):
    await bot.send_message(message.chat.id, texts.help_command)


default_commands = [
    BotCommand('start', 'Start'),
    BotCommand('help', 'Help'),
    BotCommand('my_stops', 'My saved stops')
]
