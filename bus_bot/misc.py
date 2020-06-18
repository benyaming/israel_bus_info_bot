import logging
import asyncio

from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from .config import TOKEN


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bus_bot')

loop = asyncio.get_event_loop()
bot = Bot(TOKEN, parse_mode=types.ParseMode.MARKDOWN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
