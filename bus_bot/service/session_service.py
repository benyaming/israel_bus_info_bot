import asyncio
from typing import Optional, Dict
from datetime import datetime as dt

from aiogram.types import User
from pydantic import BaseModel

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
    next_station_code: Optional[int]
    updates_count = UPDATES_COUNT
    updated_at: float = 1

    async def run_update(self, is_last_update: bool = False):
        ...

    def refresh(self):
        if not self.next_station_code:
            return
        self.station_code = self.next_station_code
        self.next_station_code = None
        self.updates_count = UPDATES_COUNT


class WatcherRepository:
    # async def get_watcher(self, user_id: int):
    #     ...
    __storage: Dict[int, Watcher] = {}

    async def save_watcher(self, watcher: Watcher):
        self.__storage[watcher.user_id] = watcher

    async def get_watcher(self, user_id: int) -> Optional[Watcher]:
        return self.__storage.get(user_id)

    async def delete_watcher(self, user_id: int):
        del self.__storage[user_id]

    # async def get_all_watchers(self) -> List[Watcher]:
    #     ...

    async def get_oldest_watcher(self) -> Optional[Watcher]:
        if len(self.__storage) == 0:
            return None
        oldest_watcher = min(self.__storage.values(), key=lambda w: w.updated_at)
        return oldest_watcher



class Limiter:
    __slots__ = ('__quantity', '__period', '__values')

    def __init__(self, quantity: int, period: float):
        self.__quantity = quantity
        self.__period = period
        self.__values = dict()

    def check(self) -> bool:
        return True

    def put(self):
        ...


limiter = Limiter(300, 5)


class Worker:
    watcher_repository = WatcherRepository()
    period: int = PERIOD

    async def _process_watcher(self, watcher: Watcher):
        if watcher.updated_at == 0:
            await watcher.run_update(is_last_update=True)
            await self.watcher_repository.delete_watcher(watcher.user_id)
        elif watcher.next_station_code:
            await watcher.run_update(is_last_update=True)
            watcher.refresh()
        else:
            await watcher.run_update()

        watcher.updates_count -= 1
        if watcher.updates_count == 0:
            watcher.updated_at = 0
        else:
            watcher.updated_at = dt.now().timestamp()

    async def run_worker(self):
        while True:
            if not limiter.check():
                await asyncio.sleep(0.1)
                continue

            watcher = await self.watcher_repository.get_oldest_watcher()
            if not watcher:
                await asyncio.sleep(0.1)
                continue

            try:
                await self._process_watcher(watcher)
            finally:
                limiter.put()

    async def add_watch(self, station_code: int):
        user_id = User.get_current().id
        watcher = Watcher(user_id=user_id, station_code=station_code)
        await self.watcher_repository.save_watcher(watcher)

    async def remove_watch(self):
        user_id = User.get_current().id
        watcher = await self.watcher_repository.get_watcher(user_id)
        if not watcher:
            # todo
            raise ValueError('no watcher found')
        watcher.updated_at = 0
        await self.watcher_repository.save_watcher(watcher)

