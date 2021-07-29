from abc import ABC
from datetime import datetime as dt
from typing import Optional

from odmantic import Model, Field, EmbeddedModel


class PersonalDetails(EmbeddedModel, ABC):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    locale: Optional[str] = None


class User(Model, ABC):
    id: int = Field(..., primary_field=True)
    language: str = 'en'
    last_seen: dt
    personal_details: PersonalDetails
