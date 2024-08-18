import asyncio
from contextlib import suppress
from time import monotonic
from datetime import datetime as dt

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import User
from httpx import AsyncClient
from pydantic import BaseModel
import betterlogging as logging

from bus_bot.config import env
from bus_bot.clients.bus_api import prepare_station_schedule
from bus_bot.keyboards import get_kb_for_stop
from bus_bot.repository.user_repository import DbRepo

UPDATES_COUNT = env.TTL // env.PERIOD


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# class BaseWatcher(BaseModel):
#     user: User
#     message_id: int
#     updates_count = UPDATES_COUNT
#     updated_at: float = 1
#
#     def run_update(self, is_last_update: bool = False):
#         raise NotImplemented


class Watcher:
    user: User
    stop_code: int
    message_id: int
    updates_count: int = UPDATES_COUNT
    updated_at: float = 1
    bot: Bot
    db_repo: DbRepo
    session: AsyncClient

    async def run_update(self, is_last_update: bool = False):
        logger.trace(f'Updating watcher: {self.user=}, {self.message_id=}')
        content = await prepare_station_schedule(self.stop_code, self.session, is_last_update)
        user = await self.db_repo.get_user(self.user)

        is_stop_saved = user.is_stop_already_saved(self.stop_code)
        kb = get_kb_for_stop(self.stop_code, is_saved=is_stop_saved) if not is_last_update else None

        try:
            await self.bot.edit_message_text(content, chat_id=self.user.id, message_id=self.message_id, reply_markup=kb)
        except TelegramBadRequest:  # todo check error status code
            pass


class WatcherRepository:
    __storage: dict[int, Watcher] = {}

    async def save_watcher(self, watcher: Watcher):
        self.__storage[watcher.message_id] = watcher

    async def get_watcher(self, message_id: int) -> Watcher | None:
        return self.__storage.get(message_id)

    async def find_watchers_by_user_id(self, user_id: int) -> list[Watcher]:
        return list(filter(lambda w: w.user.id == user_id, self.__storage.values()))  # todo fixme

    async def delete_watcher(self, message_id: int):
        del self.__storage[message_id]

    async def get_situable_watcher(self) -> Watcher | None:
        if len(self.__storage) == 0:
            return None

        oldest_watcher = min(self.__storage.values(), key=lambda w: w.updated_at)
        if dt.now().timestamp() - oldest_watcher.updated_at >= env.PERIOD:
            return oldest_watcher


class Limiter:
    __slots__ = ('__quantity', '__period', '__values')

    def __init__(self, quantity: int, period: float):
        self.__quantity = quantity
        self.__period = period
        self.__values = []

    def check(self) -> bool:
        current = monotonic()
        d = current - self.__period

        self.__values = [v for v in self.__values if v > d]

        return len(self.__values) < self.__quantity

    def put(self):
        self.__values.append(monotonic())


limiter = Limiter(env.THROTTLE_QUANTITY, env.THROTTLE_PERIOD)


class WatcherManager:
    watcher_repository = WatcherRepository()
    period: int = env.PERIOD

    __worker: asyncio.Task

    __to_delete: set[int] = set()

    async def _process_watcher(self, watcher: Watcher):
        if watcher.updated_at == 0:
            await watcher.run_update(is_last_update=True)
            await self.watcher_repository.delete_watcher(watcher.message_id)
            return

        await watcher.run_update()

        watcher.updates_count -= 1

        if watcher.updates_count < 1:
            watcher.updated_at = 0
        else:
            watcher.updated_at = dt.now().timestamp()

        await self.watcher_repository.save_watcher(watcher)

    async def _run_worker(self):
        while True:
            if not limiter.check():
                logger.warning('Trottling limit reached, skip iteration...')
                await asyncio.sleep(0.1)
                continue

            for message_id in self.__to_delete.copy():
                try:
                    w = await self.watcher_repository.get_watcher(message_id)
                    if not w:
                        logger.warning('Failed to get the worker for deletion!')
                    else:
                        w.updated_at = 0
                        await self.watcher_repository.save_watcher(w)
                except Exception as e:
                    logger.exception(f'Error while processting deletion: {repr(e)}')
                else:
                    self.__to_delete.remove(message_id)

            watcher = await self.watcher_repository.get_situable_watcher()
            if not watcher:
                await asyncio.sleep(0.1)
                continue

            try:
                await self._process_watcher(watcher)
            except Exception as e:
                logger.exception(e)
            finally:
                limiter.put()

    def run_in_background(self):
        self.__worker = asyncio.create_task(self._run_worker())

    async def close(self):
        self.__worker.cancel()
        with suppress(asyncio.CancelledError):
            await self.__worker

    async def add_watch(
            self,
            user: User,
            stop_code: int,
            message_id: int,
            bot: Bot,
            db_repo: DbRepo,
            session: AsyncClient
    ):
        active_watchers = await self.watcher_repository.find_watchers_by_user_id(user.id)
        for watcher in active_watchers:
            self.remove_watch(watcher.message_id)

        now = dt.now().timestamp()
        watcher = Watcher(
            user=user,
            stop_code=stop_code,
            message_id=message_id,
            updated_at=now,
            bot=bot,
            db_repo=db_repo,
            session=session
        )
        await self.watcher_repository.save_watcher(watcher)

    def remove_watch(self, message_id: int):
        self.__to_delete.add(message_id)
