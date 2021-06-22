from pydantic import BaseModel, Field


class StationInfo(BaseModel):
    name: str = Field(alias='Name')


class LineInfo(BaseModel):
    destination: str = Field(alias='DestinationQuarterName')
    minutes_to_arrival: int = Field(alias='MinutesToArrival')
    bus_number: str = Field(alias='Shilut')
