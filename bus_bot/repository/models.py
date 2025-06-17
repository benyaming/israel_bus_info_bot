
from datetime import datetime as dt
from typing import Optional  # Odmantic still doesn't support the | operator for Optional types

from odmantic import Model, Field, EmbeddedModel


class PersonalDetails(EmbeddedModel):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    locale: Optional[str] = None


class SavedStop(EmbeddedModel):
    name: str
    id: int


class User(Model):
    id: int = Field(..., primary_field=True)
    language: str = 'en'
    last_seen: dt = Field(default_factory=dt.now)
    personal_details: PersonalDetails
    saved_stops: list[SavedStop] = Field(default_factory=list)

    def is_stop_already_saved(self, stop_id: int) -> bool:
        return any([stop for stop in self.saved_stops if stop.id == stop_id])
