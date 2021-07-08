import logging

import aiogram_metrics

from bus_bot.config import DOCKER_MODE, WEBHOOK_URL
from bus_bot.misc import bot


logger = logging.getLogger(__file__)


async def on_start(_):
    logger.info('STARTING BUS BOT...')
    if DOCKER_MODE:
        await bot.set_webhook(WEBHOOK_URL)
    # db_conn = await aiopg.create_pool(dsn=DSN)
    # dispatcher['db_pool'] = db_conn
    #
    # await aiogram_metrics.register(METRICS_DSN, METRICS_TABLE_NAME)


async def on_shutdown(_):
    logger.info('SHUTTING DOWN...')
    await aiogram_metrics.close()
