from abc import ABC
from typing import List

from odmantic import Model, Field


class User(Model, ABC):
    id: int = Field(..., primary_field=True)
    saved_stops: List[int]
    board_set: List[int]
    language: str = 'en'
