from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bus_bot import texts
from bus_bot.states import RenameStopState
from bus_bot.repository.user_repository import DbRepo


async def on_stop_rename(msg: Message, state: FSMContext, db_repo: DbRepo, bot: Bot):
    state_data: dict = (await state.get_data()).get('stop_rename')
    if not state_data:
        await state.clear()
        raise RuntimeError('No state data found')

    if msg.text == texts.done_button:
        stop_name = state_data.get('name')
    else:
        stop_name = msg.text

    await db_repo.save_stop(msg.from_user, state_data.get('code'), stop_name)
    await msg.reply(texts.stop_saved.format(stop_name), reply_markup=ReplyKeyboardRemove())

    await state.clear()


router = Router()
router.message.register(on_stop_rename, RenameStopState.waiting_for_stop_name)
