import logging

import aiogram_metrics

from bus_bot import misc
from bus_bot.config import DOCKER_MODE, WEBHOOK_URL
from bus_bot.handlers.commands import default_commands

logger = logging.getLogger(__name__)


async def on_start(_):
    logger.info('STARTING BUS BOT...')
    if DOCKER_MODE:
        await misc.bot.set_webhook(WEBHOOK_URL)

    misc.watcher_manager.run_in_background()
    await misc.bot.set_my_commands(default_commands)


async def on_shutdown(_):
    logger.info('SHUTTING DOWN...')
    await misc.watcher_manager.close()
    await aiogram_metrics.close()
