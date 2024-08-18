import aiogram_metrics
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bus_bot import texts


@aiogram_metrics.track('Unknown message')
async def incorrect_message_handler(msg: Message):
    await msg.reply(texts.incorrect_message)


@aiogram_metrics.track('Cancel')
async def on_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.reply(texts.cancel, reply_markup=ReplyKeyboardRemove())
