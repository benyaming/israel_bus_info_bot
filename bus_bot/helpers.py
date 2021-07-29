from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class CallbackPrefix:
    stop_updates = 'stop_updates:'
    get_stop = 'stop:'


def get_cancel_button(station: int) -> InlineKeyboardMarkup:
    """
    Return inline keyboard with 'Stop tracking' button
    :return:
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Stop updating', callback_data=f'{CallbackPrefix.stop_updates}{station}'))
    return keyboard
