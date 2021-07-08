import asyncio
from typing import Optional, Dict, List

from aiogram.utils.exceptions import MessageNotModified
from aiogram.types import User, Message
from pydantic import BaseModel

from bus_bot.core.bus_api_v3.client import prepare_station_schedule
from bus_bot.helpers import get_cancel_button
from bus_bot.misc import bot
from bus_bot.config import TTL, PERIOD

UPDATES_COUNT = TTL // PERIOD


# class Session:
#     user_id: int
#     msg_id: int
#     next_msg_id: Optional[int] = None
#     current_station: int
#     next_station: Optional[int] = None
#     updates_count = UPDATES_COUNT
#
#     def __init__(self, user_id: int, station: int):
#         self.user_id = user_id
#         self.current_station = station
#
#     async def init(self):
#         while True:
#             if self.next_station:
#                 asyncio.create_task(
#                     self.update_message(is_last_update=True)
#                 )
#                 self.reset()
#
#             await asyncio.sleep(PERIOD)
#
#             if self.updates_count > 0:
#                 await self.update_message()
#                 self.updates_count -= 1
#             elif self.updates_count == 0:
#                 await self.update_message(is_last_update=True)
#                 break
#
#     def reset(self):
#         self.updates_count = UPDATES_COUNT
#         self.current_station = self.next_station
#         self.msg_id = self.next_msg_id
#         self.next_msg_id = None
#         self.next_station = None
#
#     async def update_message(self, is_last_update: bool = False):
#         content = await prepare_station_schedule(self.current_station, is_last_update)
#         kb = get_cancel_button(self.current_station) if not is_last_update else None
#
#         try:
#             await bot.edit_message_text(content, self.user_id, self.msg_id, reply_markup=kb)
#         except MessageNotModified:
#             pass


class Watcher(BaseModel):
    user_id: int
    station_code: int
    is_ready_for_delete: bool = False
    next_station_code: Optional[int]
    updates_count = UPDATES_COUNT

    async def run_update(self):
        ...

    def refresh(self):
        if not self.next_station_code:
            return
        self.station_code = self.next_station_code
        self.next_station_code = None
        self.updates_count = UPDATES_COUNT


class WatcherRepository:
    async def get_watcher(self, user_id: int):
        ...

    async def save_watcher(self, watcher: Watcher):
        ...

    async def delete_watcher(self, user_id: int):
        ...


    async def get_all_watchers(self) -> List[Watcher]:
        ...


class SessionRunner:
    watcher_repository: WatcherRepository
    period: int = PERIOD

    async def update_infinite(self):
        while True:
            for watcher in await self.watcher_repository.get_all_watchers():
                await watcher.run_update()

                if watcher.is_ready_for_delete:
                    await self.watcher_repository.delete_watcher(watcher.user_id)
                elif watcher.next_station_code:
                    watcher.refresh()
                    await watcher.run_update()

    async def start_watch(self, station_code: int):
        user_id = User.get_current().id
        watcher = Watcher(user_id=user_id, station_code=station_code)
        await self.watcher_repository.save_watcher(watcher)

    async def stop_watch(self):
        user_id = User.get_current().id
        watcher = self.watcher_repository.get_watcher(user_id)

