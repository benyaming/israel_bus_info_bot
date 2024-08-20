from aiogram.fsm.state import StatesGroup, State


class RenameStopState(StatesGroup):
    waiting_for_stop_name = State()
