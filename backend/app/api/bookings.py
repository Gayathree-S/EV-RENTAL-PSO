"""
EV Booking and Reservation API routes — Task 9.
Integrates with Task 7 ML demand prediction model.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.booking import Booking
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.booking import BookingCreateRequest, BookingOut
from app.services.prediction_model import predict_charging_energy

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vehicle booking with ML-predicted charging demand",
)
def create_booking(req: BookingCreateRequest, db: Session = Depends(get_db)):
    # 1. Verify User exists
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {req.user_id} not found",
        )

    # 2. Verify Vehicle exists and is available
    vehicle = db.query(Vehicle).filter(Vehicle.id == req.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {req.vehicle_id} not found",
        )
    if not vehicle.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle {vehicle.vehicle_code} is currently not available",
        )

    # 3. Predict charging energy requirement (Task 7 ML model)
    try:
        predicted_energy = predict_charging_energy(
            dropoff_time_hr=req.dropoff_time_hr,
            pickup_time_hr=req.pickup_time_hr,
        )
    except Exception as e:
        predicted_energy = None

    # 4. Create booking and mark vehicle as reserved
    booking = Booking(
        user_id=req.user_id,
        vehicle_id=req.vehicle_id,
        dropoff_time_hr=req.dropoff_time_hr,
        pickup_time_hr=req.pickup_time_hr,
        predicted_charging_energy_kwh=predicted_energy,
    )
    vehicle.is_available = False

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


@router.get(
    "",
    response_model=List[BookingOut],
    summary="Get all bookings sorted newest first (Admin view)",
)
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).order_by(Booking.created_at.desc(), Booking.id.desc()).all()
    return bookings


@router.get(
    "/user/{user_id}",
    response_model=List[BookingOut],
    summary="Get all bookings for a specific user",
)
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc(), Booking.id.desc())
        .all()
    )
    return bookings
