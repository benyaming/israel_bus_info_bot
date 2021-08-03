import logging

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from aiogram.utils.executor import start_webhook, start_polling

from bus_bot.handlers import register_handlers
from bus_bot.middleware import register_middlewares
from bus_bot.misc import dp
from bus_bot.handlers.bot_lifecycle_hooks import on_start, on_shutdown
from bus_bot.config import env
from bus_bot.middleware.sentry_middleware import SentryContextMiddleware

logger = logging.getLogger('bot')


if env.SENTRY_KEY:
    sentry_sdk.init(
        dsn=env.SENTRY_KEY,
        integrations=[AioHttpIntegration()]
    )
logger.info(f'Sentry is {"ENABLED" if env.SENTRY_KEY else "DISABLED"}')

dp.middleware.setup(SentryContextMiddleware())


if __name__ == '__main__':
    register_handlers()
    register_middlewares()

    if env.DOCKER_MODE:
        start_webhook(
            dispatcher=dp,
            webhook_path=env.WEBHOOK_PATH,
            host=env.WEBAPP_HOST,
            port=env.WEBAPP_PORT,
            skip_updates=True,
            on_startup=on_start,
            on_shutdown=on_shutdown
        )
    else:
        start_polling(dp, on_startup=on_start)
