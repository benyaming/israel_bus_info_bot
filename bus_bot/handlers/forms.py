from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bus_bot import texts
from bus_bot.keyboards import get_kb_for_stop
from bus_bot.misc import bot
from bus_bot.repository import user_repository


async def on_stop_rename(msg: Message, state: FSMContext):
    state_data: dict = (await state.get_data()).get('stop_rename')
    if not state_data:
        await state.finish()
        raise RuntimeError('No state data found')

    # origin_message_id = state_data.get('origin')

    # kb = get_kb_for_stop(stop_code=state_data.get('code'), is_saved=True)
    # await bot.edit_message_reply_markup(msg.from_user.id, origin_message_id, reply_markup=kb)

    if msg.text == texts.done_button:
        stop_name = state_data.get('name')
    else:
        stop_name = msg.text

    await user_repository.save_stop(msg.from_user.id, state_data.get('code'), stop_name)
    await msg.reply(texts.stop_saved.format(stop_name), reply_markup=ReplyKeyboardRemove())

    await state.finish()
