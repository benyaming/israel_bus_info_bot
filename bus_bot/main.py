import logging

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from aiogram.utils.executor import start_webhook, start_polling

import bus_bot.handlers
from bus_bot.misc import dp
from bus_bot.handlers.bot_lifecycle_hooks import on_start, on_shutdown
from bus_bot.config import (
    DOCKER_MODE,
    WEBAPP_PORT,
    WEBAPP_HOST,
    WEBHOOK_PATH,
    PERIOD,
    TTL,
    SENTRY_KEY
)
from bus_bot.sentry_middleware import SentryContextMiddleware

logger = logging.getLogger('bot')


ITERATIONS = TTL // PERIOD

if SENTRY_KEY:
    sentry_sdk.init(
        dsn=SENTRY_KEY,
        integrations=[AioHttpIntegration()]
    )
logger.info(f'Sentry is {"ENABLED" if SENTRY_KEY else "DISABLED"}')

dp.middleware.setup(SentryContextMiddleware())




# @dp.message_handler()
# @aiogram_metrics.track('Unknown message')
# async def incorrect_message_handler(msg: Message):
#     await msg.reply(texts.incorrect_message)





if __name__ == '__main__':
    if DOCKER_MODE:

        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
            skip_updates=True,
            on_startup=on_start,
            on_shutdown=on_shutdown
        )
    else:
        start_polling(dp, on_startup=on_start)


# TODO - REFACTOR IT!!!
