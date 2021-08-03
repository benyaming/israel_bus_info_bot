import aiogram_metrics
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, BotCommand

from bus_bot import texts
from bus_bot.keyboards import get_saved_stops_kb
from bus_bot.misc import bot
from bus_bot.repository import user_repository


@aiogram_metrics.track('/start command')
async def on_start_command(msg: Message, state: FSMContext):
    await state.finish()
    await bot.send_message(msg.chat.id, texts.start_command)


@aiogram_metrics.track('/help command')
async def on_help_command(message: Message):
    await bot.send_message(message.chat.id, texts.help_command)


async def on_saved_stops_command(msg: Message):
    saved_stops = await user_repository.get_user_saved_stops(msg.from_user.id)
    if not saved_stops:
        return await msg.reply(texts.saved_stops_emply_list)

    kb = get_saved_stops_kb(saved_stops)
    await msg.reply(texts.here_is_your_stops, reply_markup=kb)


default_commands = [
    BotCommand('start', 'Start'),
    BotCommand('help', 'Help'),
    BotCommand('my_stops', 'My saved stops')
]
