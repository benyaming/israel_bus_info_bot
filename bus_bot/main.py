import asyncio
import httpx
import os

import aiogram_metrics
import sentry_sdk
import betterlogging as bl
from aiohttp import web
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from motor.motor_asyncio import AsyncIOMotorClient
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from bus_bot.handlers import register_handlers
from bus_bot.middleware import register_middlewares
from bus_bot.handlers.commands import DEFAULT_COMMANDS
from bus_bot.config import env
from bus_bot.repository.user_repository import DbRepo
from bus_bot.service.watcher_management_service import WatcherManager


bl.basic_colorized_config(level=bl.INFO)
logger = bl.getLogger('bot')


if env.SENTRY_KEY:
    sentry_sdk.init(
        dsn=env.SENTRY_KEY,
        integrations=[AioHttpIntegration()]
    )
logger.info(f'Sentry is {"ENABLED" if env.SENTRY_KEY else "DISABLED"}')


async def on_start(bot: Bot):
    logger.info('STARTING BUS BOT...')
    if env.DOCKER_MODE:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(env.WEBHOOK_URL)

    if env.METRICS_DSN and env.METRICS_TABLE_NAME:
        await aiogram_metrics.register(env.METRICS_DSN, env.METRICS_TABLE_NAME)

    await bot.set_my_commands(DEFAULT_COMMANDS)


async def main():

    motor_client = AsyncIOMotorClient(env.DB_URL)
    storage = MongoStorage(client=motor_client, db_name=env.DB_NAME, collection_name=env.DB_COLLECTION_NAME)
    db_repo = DbRepo(motor_client)

    session = httpx.AsyncClient()
    wm = WatcherManager()
    wm.run_in_background()

    dp = Dispatcher(
        storage=storage,

        # context objects
        db_repo=db_repo,
        http_client=session,
        watcher_manager=wm,
    )

    register_handlers(dp)
    register_middlewares(dp)

    bot = Bot(env.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

    dp.startup.register(on_start)

    if env.DOCKER_MODE:
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=env.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        web.run_app(app, host=env.WEBAPP_HOST, port=env.WEBAPP_PORT)
    else:
        await dp.start_polling(bot)


if __name__ == '__main__':
    if os.name == 'nt':
        from asyncio import WindowsSelectorEventLoopPolicy

        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
