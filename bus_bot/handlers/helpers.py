import aiogram_metrics
from aiogram.types import Message

from bus_bot import texts


@aiogram_metrics.track('Unknown message')
async def incorrect_message_handler(msg: Message):
    await msg.reply(texts.incorrect_message)
