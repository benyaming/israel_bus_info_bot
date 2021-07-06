from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class IncomingRoutesResponse(BaseModel):
    response_time: datetime = Field(default_factory=datetime.now)
    stop_info: 'Stop'
    incoming_routes: List['IncomingRoute']


class Stop(BaseModel):
    id: int
    code: int
    name: str
    city: str
    street: Optional[str] = None
    floor: Optional[str] = None
    platform: Optional[str] = None
    location: 'StopLocation'
    location_type: str
    parent_station_id: Optional[str] = None
    zone_id: Optional[str] = None


class Route(BaseModel):
    id: str
    agency_id: str
    short_name: str
    from_stop_name: str
    to_stop_name: str
    from_city: str
    to_city: str
    description: str
    type: str
    color: str


class IncomingRoute(BaseModel):
    eta: int
    route: 'Route'


class StopLocation(BaseModel):
    type: str = 'Point'
    coordinates: Tuple[float, float]


IncomingRoutesResponse.update_forward_refs()
Stop.update_forward_refs()

