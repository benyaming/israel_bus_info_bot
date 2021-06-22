import asyncio

import betterlogging as bl
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from .config import TOKEN

bl.basic_colorized_config(level=bl.INFO)
logger = bl.getLogger('bus_bot')

loop = asyncio.get_event_loop()
bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
session = dp.bot.session
