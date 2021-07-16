from ..misc import dp

from .bus_handlers import *
from .bot_lifecycle_hooks import *
from . import commands
from .errors import *


dp.register_message_handler(commands.handle_start, commands=['start'])
