from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


__all__ = ['Stop', 'Route', 'IncomingRoute', 'IncomingRoutesResponse', 'StopLocation']


class Agency(BaseModel):
    id: int
    name: str
    url: str
    phone: str


class Route(BaseModel):
    id: str
    agency: Agency
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
    route: Route


class StopLocation(BaseModel):
    type: str = 'Point'
    coordinates: list[float]


class Stop(BaseModel):
    id: int
    code: int
    name: str
    city: str | None
    street: str | None = None
    floor: str | None = None
    platform: str | None = None
    location: StopLocation
    location_type: str
    parent_station_id: str | None = None
    zone_id: str | None = None


class IncomingRoutesResponse(BaseModel):
    response_time: datetime = Field(default_factory=datetime.now)
    stop_info: Stop
    incoming_routes: list[IncomingRoute]
