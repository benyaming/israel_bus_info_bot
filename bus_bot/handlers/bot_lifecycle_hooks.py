import logging

import aiogram_metrics
from aiogram import Dispatcher

from bus_bot import misc
from bus_bot.config import DOCKER_MODE, WEBHOOK_URL, METRICS_DSN, METRICS_TABLE_NAME
from bus_bot.handlers.commands import default_commands
from bus_bot.service.watcher_management_service import WatcherManager

logger = logging.getLogger(__name__)


async def on_start(dp: Dispatcher):
    logger.info('STARTING BUS BOT...')
    if DOCKER_MODE:
        await misc.bot.set_webhook(WEBHOOK_URL)
    if METRICS_DSN and METRICS_TABLE_NAME:
        await aiogram_metrics.register(METRICS_DSN, METRICS_TABLE_NAME)

    dp['watcher_manager'] = WatcherManager()
    dp['watcher_manager'].run_in_background()
    await misc.bot.set_my_commands(default_commands)


async def on_shutdown(dp: Dispatcher):
    logger.info('SHUTTING DOWN...')
    await dp['watcher_manager'].watcher_manager.close()
    await aiogram_metrics.close()
