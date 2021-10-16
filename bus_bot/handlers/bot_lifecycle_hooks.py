import logging

import aiogram_metrics
from aiogram import Dispatcher

from bus_bot import misc
from bus_bot.config import env
from bus_bot.handlers.commands import default_commands
from bus_bot.service.watcher_management_service import WatcherManager

logger = logging.getLogger(__name__)


async def on_start(dp: Dispatcher):
    logger.info('STARTING BUS BOT...')
    if env.DOCKER_MODE:
        await misc.bot.set_webhook(env.WEBHOOK_URL)
    if env.METRICS_DSN and env.METRICS_TABLE_NAME:
        await aiogram_metrics.register(env.METRICS_DSN, env.METRICS_TABLE_NAME)

    dp['watcher_manager'] = WatcherManager()
    dp['watcher_manager'].run_in_background()
    await misc.bot.set_my_commands(default_commands)


async def on_shutdown(dp: Dispatcher):
    logger.info('SHUTTING DOWN...')
    await misc.session.aclose()
    await dp['watcher_manager'].close()
    await aiogram_metrics.close()
