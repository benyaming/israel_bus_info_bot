import logging

import aiogram_metrics
from aiogram.types import ContentTypes, Message

from bus_bot.core.bus_api_v3.client import prepare_station_schedule
from bus_bot.helpers import get_cancel_button
from bus_bot.misc import dp, bot, update_service


logger = logging.getLogger('bot')


@dp.message_handler(lambda msg: msg.text.isdigit(), content_types=ContentTypes.TEXT)
async def station_handler(msg: Message):
    station_id = int(msg.text)

    content = await prepare_station_schedule(station_id)
    kb = get_cancel_button(msg.text)
    sent = await msg.reply(content, reply_markup=kb)
    aiogram_metrics.manual_track('Init station schedule')

    await update_service.add_watch(station_id, sent.message_id)
