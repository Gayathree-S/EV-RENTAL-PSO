"""
RentalCenter and Vehicle schemas.
"""

from typing import List
from pydantic import BaseModel, ConfigDict


class VehicleOut(BaseModel):
    id: int
    center_id: int
    vehicle_code: str
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


class RentalCenterOut(BaseModel):
    id: int
    bus_number: int
    name: str
    max_fleet_size: int
    vehicles: List[VehicleOut] = []

    model_config = ConfigDict(from_attributes=True)
