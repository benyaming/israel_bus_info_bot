import aiogram_metrics
from aiogram import Router, F
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


cancel_router = Router()
cancel_router.message.register(incorrect_message_handler, F.text.startswith(texts.cancel_button))

incorrect_message_router = Router()
incorrect_message_router.message.register(on_cancel)

