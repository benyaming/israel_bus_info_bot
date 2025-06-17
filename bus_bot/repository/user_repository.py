from datetime import datetime as dt

import aiogram_metrics
from aiogram.types import User as TelegramUser, Update
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from bus_bot.config import env
from bus_bot.exceptions import StopAlreadySaved
from bus_bot.repository.models import User, PersonalDetails, SavedStop


class DbRepo:
    _db: AIOEngine | None

    @property
    def db(self) -> AIOEngine:
        if not self._db:
            raise RuntimeError('DB is not initialized!')
        return self._db

    @db.setter
    def db(self, engine: AIOEngine):
        self._db = engine

    def __init__(self, motor_client: AsyncIOMotorClient):
        self.db = AIOEngine(motor_client, database=env.DB_NAME)

    async def check_user(self, tg_user: TelegramUser, event: Update | None = None) -> None:
        user = await self.db.find(User, User.id == tg_user.id)

        if user:
            user = user[0]
            user.last_seen = dt.now()
        else:
            pd = PersonalDetails(
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                username=tg_user.username,
                locale=tg_user.language_code
            )
            user = User(id=tg_user.id, personal_details=pd)

            aiogram_metrics.manual_track('New user Joined', update=event, user_id=tg_user.id)

        await self.db.save(user)

    async def get_user(self, tg_user: TelegramUser) -> User:
        user = await self.db.find(User, User.id == tg_user.id)
        if not user:
            await self.check_user(tg_user)
            return await self.get_user(tg_user)  # todo check if it's ok to call itself
        return user[0]

    # Saved stops management
    async def get_user_saved_stops(self, tg_user: TelegramUser) -> list[SavedStop]:
        user = await self.get_user(tg_user)
        return user.saved_stops

    async def save_stop(self, tg_user: TelegramUser, stop_id: int, stop_name: str) -> list[SavedStop]:
        user = await self.get_user(tg_user)

        stop = SavedStop(name=stop_name, id=stop_id)
        if user.is_stop_already_saved(stop_id):
            raise StopAlreadySaved()

        user.saved_stops.append(stop)

        await self.db.save(user)
        return user.saved_stops

    async def rename_stop(self, tg_user: TelegramUser, stop_id: int, new_name: str) -> list[SavedStop]:
        user = await self.get_user(tg_user)
        stop = list(filter(lambda s: s.id == stop_id, user.saved_stops))
        if not stop:
            raise ValueError('Trying to update non-existing saved stop!')

        stop = stop[0]
        stop_index = user.saved_stops.index(stop)
        user.saved_stops[stop_index].name = new_name
        await self.db.save(user)
        return user.saved_stops

    async def remove_stop(self, tg_user: TelegramUser, stop_id: int) -> list[SavedStop]:
        user = await self.get_user(tg_user)
        stop = list(filter(lambda s: s.id == stop_id, user.saved_stops))
        if not stop:
            raise ValueError('Trying to delete non-existing saved stop!')

        stop = stop[0]
        user.saved_stops.remove(stop)
        await self.db.save(user)
        return user.saved_stops
