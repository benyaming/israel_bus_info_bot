from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


__all__ = ['Stop', 'Route', 'IncomingRoute', 'IncomingRoutesResponse', 'StopLocation', 'StopType']


class StopType(StrEnum):
    bus_stop = 'bus_stop'
    bus_central_station = 'bus_central_station'
    bus_central_station_platform = 'bus_central_station_platform'
    jerusalem_light_rail_stop = 'jerusalem_light_rail_stop'
    gush_dan_light_rail_station = 'gush_dan_light_rail_station'
    gush_dan_light_rail_platform = 'gush_dan_light_rail_platform'
    railway_station = 'railway_station'


class Agency(BaseModel):
    id: int
    name: str
    url: str
    phone: str


class Route(BaseModel):
    id: int
    agency: Agency
    short_name: str
    from_stop_name: str
    to_stop_name: str
    from_city: str
    to_city: str
    description: str
    type: int
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
    floor: int | None = None
    platform: int | None = None
    location: StopLocation
    location_type: int
    parent_station_id: int | None = None
    zone_id: int | None = None
    stop_type: StopType = StopType.bus_stop


class IncomingRoutesResponse(BaseModel):
    response_time: datetime = Field(default_factory=datetime.now)
    stop_info: Stop
    incoming_routes: list[IncomingRoute]
