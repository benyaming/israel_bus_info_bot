import asyncio

import betterlogging as bl
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from motor.core import AgnosticCollection
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from .config import TOKEN, DB_URL, DB_NAME, DB_COLLECTION_NAME


bl.basic_colorized_config(level=bl.INFO)

loop = asyncio.get_event_loop()
bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
session = dp.bot.session

motor_client = AsyncIOMotorClient(DB_URL)
collection: AgnosticCollection = motor_client[DB_NAME][DB_COLLECTION_NAME]
db_engine = AIOEngine(motor_client, database=DB_NAME)
