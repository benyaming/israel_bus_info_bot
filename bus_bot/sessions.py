from __future__ import annotations
from typing import Optional, Dict

from .config import PERIOD, TTL


SESSION_STORAGE: Dict[int, Session] = {}


class Session:
    user_id: int
    msg_id: int
    next_msg_id: Optional[int] = None
    current_station: int
    next_station: Optional[int] = None
    # expired = False
    updates_count: int

    def __init__(self, user_id: int, station: int):
        self.user_id = user_id
        self.current_station = station
        self.updates_count = TTL // PERIOD

        SESSION_STORAGE[user_id] = self

    def reset(self):
        self.updates_count = TTL // PERIOD
        self.current_station = self.next_station
        self.msg_id = self.next_msg_id
        self.next_msg_id = None
        self.next_station = None



