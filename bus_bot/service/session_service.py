import asyncio
import logging
from typing import Optional, Dict
from datetime import datetime as dt

from aiogram import Bot
from aiogram.types import User
from aiogram.utils.exceptions import MessageNotModified
from pydantic import BaseModel

from bus_bot.config import TTL, PERIOD
from bus_bot.core.bus_api_v3.client import prepare_station_schedule
from bus_bot.helpers import get_cancel_button

UPDATES_COUNT = TTL // PERIOD


class Watcher(BaseModel):
    user_id: int
    station_code: int
    message_id: int
    next_station_code: Optional[int]
    next_message_id: Optional[int]
    updates_count = UPDATES_COUNT
    updated_at: float = 1

    async def run_update(self, is_last_update: bool = False):
        content = await prepare_station_schedule(self.station_code, is_last_update)
        bot = Bot.get_current()
        kb = get_cancel_button(self.station_code) if not is_last_update else None

        try:
            await bot.edit_message_text(content, self.user_id, self.message_id, reply_markup=kb)
        except MessageNotModified:
            pass

    def refresh(self):
        if not self.next_station_code or not self.next_message_id:
            return
        self.station_code = self.next_station_code
        self.message_id = self.next_message_id
        self.next_station_code = None
        self.next_message_id = None
        self.updates_count = UPDATES_COUNT


class WatcherRepository:
    __storage: Dict[int, Watcher] = {}

    async def save_watcher(self, watcher: Watcher):
        self.__storage[watcher.user_id] = watcher

    async def get_watcher(self, user_id: int) -> Optional[Watcher]:
        return self.__storage.get(user_id)

    async def delete_watcher(self, user_id: int):
        del self.__storage[user_id]

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

    __worker: asyncio.Task

    async def _process_watcher(self, watcher: Watcher):
        if watcher.updated_at == 0:
            await watcher.run_update(is_last_update=True)
            await self.watcher_repository.delete_watcher(watcher.user_id)
        elif watcher.next_station_code and watcher.next_message_id:
            await watcher.run_update(is_last_update=True)
            watcher.refresh()
        else:
            await watcher.run_update()

        watcher.updates_count -= 1
        if watcher.updates_count == 0:
            watcher.updated_at = 0
        else:
            watcher.updated_at = dt.now().timestamp()

        await self.watcher_repository.save_watcher(watcher)

    async def _run_worker(self):
        while True:
            if not limiter.check():
                await asyncio.sleep(0.1)
                continue

            watcher = await self.watcher_repository.get_oldest_watcher()
            if not watcher:
                await asyncio.sleep(0.1)
                continue

            if dt.now().timestamp() - watcher.updated_at < PERIOD:
                continue

            try:
                await self._process_watcher(watcher)
            except Exception as e:
                logging.exception(e)
            finally:
                limiter.put()

    async def run_in_background(self):
        self.__worker = asyncio.create_task(self._run_worker())

    async def add_watch(self, station_code: int, message_id: int):
        user_id = User.get_current().id

        watcher = await self.watcher_repository.get_watcher(user_id)
        if watcher:
            watcher.next_station_code = station_code
            watcher.next_message_id = message_id
        else:
            now = dt.now().timestamp()
            watcher = Watcher(user_id=user_id, station_code=station_code, message_id=message_id, updated_at=now)
        await self.watcher_repository.save_watcher(watcher)

    async def remove_watch(self):
        user_id = User.get_current().id
        watcher = await self.watcher_repository.get_watcher(user_id)
        if not watcher:
            raise ValueError('No watcher found')
        watcher.updated_at = 0
        await self.watcher_repository.save_watcher(watcher)
