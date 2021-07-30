from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bus_bot import texts
from bus_bot.helpers import CallbackPrefix


def get_kb_for_stop(stop_code: int, is_saved: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    text = texts.add_to_saved_button if not is_saved else texts.remove_from_saved_button
    cb_data = f'{CallbackPrefix.save_stop if not is_saved else CallbackPrefix.remove_stop}{stop_code}'

    kb.add(InlineKeyboardButton(text, callback_data=cb_data))
    kb.add(InlineKeyboardButton(texts.cancel_updating_button, callback_data=f'{CallbackPrefix.stop_updates}{stop_code}'))
    return kb
