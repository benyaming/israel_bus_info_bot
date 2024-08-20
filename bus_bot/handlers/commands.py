import aiogram_metrics
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand

from bus_bot import texts
from bus_bot.keyboards import get_saved_stops_kb
from bus_bot.repository.user_repository import DbRepo


DEFAULT_COMMANDS = [
    BotCommand(command='start', description='Start'),
    BotCommand(command='help', description='Help'),
    BotCommand(command='my_stops', description='My saved stops')
]


@aiogram_metrics.track('/start command')
async def on_start_command(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.send_message(message.chat.id, texts.start_command)


@aiogram_metrics.track('/help command')
async def on_help_command(message: Message, bot: Bot):
    await bot.send_message(message.chat.id, texts.help_command)


@aiogram_metrics.track('/my_stops command')
async def on_saved_stops_command(message: Message, db_repo: DbRepo):
    saved_stops = await db_repo.get_user_saved_stops(message.from_user)
    if not saved_stops:
        return await message.reply(texts.saved_stops_emply_list)

    kb = get_saved_stops_kb(saved_stops)
    await message.reply(texts.here_is_your_stops, reply_markup=kb)


router = Router()
router.message.register(on_start_command, Command('start'))
router.message.register(on_help_command, Command('help'))
router.message.register(on_saved_stops_command, Command('my_stops'))
