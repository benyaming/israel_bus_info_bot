from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from bus_bot import texts
from bus_bot.helpers import CallbackPrefix
from bus_bot.repository.models import SavedStop
from bus_bot.clients.bus_api.models import Stop


def get_kb_for_stop(stop_id: int, is_saved: bool) -> InlineKeyboardMarkup:
    text = texts.add_to_saved_button if not is_saved else texts.remove_from_saved_button
    cb_data = f'{CallbackPrefix.save_stop if not is_saved else CallbackPrefix.remove_stop}{stop_id}'

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, callback_data=cb_data),
                InlineKeyboardButton(
                    text=texts.cancel_updating_button,
                    callback_data=f'{CallbackPrefix.terminate_stop_updating}{stop_id}')
            ]
        ]
    )

    return kb


def get_done_button_with_placeholder(placeholder_text: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=placeholder_text,
        keyboard=[[KeyboardButton(text=texts.cancel_button), KeyboardButton(text=texts.done_button)]]
    )
    return kb


def get_saved_stops_kb(saved_stops: list[SavedStop]) -> InlineKeyboardMarkup:
    rows = []

    for stop in saved_stops:
        rows.append(
            [
                InlineKeyboardButton(
                    text=stop.name,
                    callback_data=f'{CallbackPrefix.get_saved_stop}{stop.id}'
                )
            ]
        )

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def get_kb_for_stops_map(stops: list[Stop]) -> InlineKeyboardMarkup:
    rows = []
    i = 1
    
    for stop in stops:
        text = f'{i} — {stop.name} ({stop.code})'
        callback_data = f'{CallbackPrefix.get_stop}{stop.id}'
        
        rows.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
        i += 1
    
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_restart_stop_updating_kb(stop_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=texts.restart_stop_updating_button,
                    callback_data=f'{CallbackPrefix.restart_stop_updating}{stop_id}'
                )
            ]
        ]
    )
    return kb


# def get_platforms_kb(stops: list[Stop]) -> InlineKeyboardMarkup:
#     rows = []
#     i = 1
#
#     for stop in stops:
#         if not stop.platform:
#             continue
#
#         text = f'{i} — {stop.name} - platform {stop.platform}'
#         callback_data = f'{CallbackPrefix.get_stop}{stop.id}'
#         rows.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
#         i += 1
#
#     rows.append([InlineKeyboardButton(text='⬅️ Back to stops', callback_data=CallbackPrefix.back_to_stops)])
#
#     return InlineKeyboardMarkup(inline_keyboard=rows)

