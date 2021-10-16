import asyncio
import httpx

import betterlogging as bl
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from motor.core import AgnosticCollection
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from .config import env


bl.basic_colorized_config(level=bl.INFO)

loop = asyncio.get_event_loop()
bot = Bot(env.TOKEN, parse_mode=types.ParseMode.HTML)
storage = MongoStorage(uri=env.DB_URL, db_name=env.DB_NAME)
dp = Dispatcher(bot, storage=storage)
session = httpx.AsyncClient()

motor_client = AsyncIOMotorClient(env.DB_URL)
collection: AgnosticCollection = motor_client[env.DB_NAME][env.DB_COLLECTION_NAME]
db_engine = AIOEngine(motor_client, database=env.DB_NAME)
