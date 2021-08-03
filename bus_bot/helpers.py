import inspect
from typing import Union, Callable, Literal

from aiogram.types import ChatActions


class CallbackPrefix:
    terminate_stop_updating = 'q_'
    get_stop = 'w_'
    get_saved_stop = 'e_'
    save_stop = 'r_'
    remove_stop = 't_'


# Warning: it is not working when using injected FSMContext state!
def chat_action(arg: Union[str, Literal['text'], Literal['image']]):
    _func = arg if arg and callable(arg) else None
    action_type = None if _func else arg

    if not _func:
        action_type = arg

    def decorator(func):

        async def wrapper(*args, **kwargs):
            chat_actions = {
                'image': ChatActions.upload_photo,
                'text': ChatActions.typing
            }
            action_func = chat_actions.get(action_type, ChatActions.typing)
            await action_func()

            spec = inspect.getfullargspec(func)
            kwargs = {k: v for k, v in kwargs.items() if k in spec.args}

            return await func(*args, **kwargs)

        return wrapper
    return decorator(_func) if _func else decorator
