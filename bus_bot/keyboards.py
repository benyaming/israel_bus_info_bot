from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from bus_bot import texts
from bus_bot.helpers import CallbackPrefix
from bus_bot.repository.models import SavedStop


def get_kb_for_stop(stop_code: int, is_saved: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    text = texts.add_to_saved_button if not is_saved else texts.remove_from_saved_button
    cb_data = f'{CallbackPrefix.save_stop if not is_saved else CallbackPrefix.remove_stop}{stop_code}'

    kb.add(InlineKeyboardButton(text, callback_data=cb_data))
    kb.add(InlineKeyboardButton(texts.cancel_updating_button,
                                callback_data=f'{CallbackPrefix.terminate_stop_updating}{stop_code}'))
    return kb


def get_done_button_with_placeholder(placeholder_text: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, input_field_placeholder=placeholder_text)
    kb.row(texts.cancel_button, texts.done_button)
    return kb


def get_saved_stops_kb(saved_stops: list[SavedStop]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    for stop in saved_stops:
        kb.row(
            InlineKeyboardButton(
                text=stop.name,
                callback_data=f'{CallbackPrefix.get_saved_stop}{stop.code}'
            )
        )
    return kb
