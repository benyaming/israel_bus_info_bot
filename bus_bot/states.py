from aiogram.dispatcher.filters.state import StatesGroup, State


class RenameStopState(StatesGroup):
    waiting_for_stop_name = State()
