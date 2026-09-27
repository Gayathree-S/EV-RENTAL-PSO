"""
Booking request and response schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserOut
from app.schemas.center import VehicleOut


class BookingCreateRequest(BaseModel):
    user_id: int
    vehicle_id: int
    dropoff_time_hr: float
    pickup_time_hr: float


class BookingOut(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    dropoff_time_hr: float
    pickup_time_hr: float
    predicted_charging_energy_kwh: Optional[float] = None
    created_at: datetime
    user: Optional[UserOut] = None
    vehicle: Optional[VehicleOut] = None

    model_config = ConfigDict(from_attributes=True)
