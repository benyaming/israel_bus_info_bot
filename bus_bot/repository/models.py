from abc import ABC
from datetime import datetime as dt
from typing import Optional, List

from odmantic import Model, Field, EmbeddedModel


class PersonalDetails(EmbeddedModel, ABC):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    locale: Optional[str] = None


class SavedStop(EmbeddedModel, ABC):
    name: str
    code: int


class User(Model, ABC):
    id: int = Field(..., primary_field=True)
    language: str = 'en'
    last_seen: dt = Field(default_factory=dt.now)
    personal_details: PersonalDetails
    saved_stops: List[SavedStop] = Field(default_factory=list)

    def is_stop_already_saved(self, stop_code: int) -> bool:
        return any([stop for stop in self.saved_stops if stop.code == stop_code])
