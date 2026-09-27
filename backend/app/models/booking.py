from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.session import Base


class Booking(Base):
    __tablename__ = "bookings"

    id                            = Column(Integer, primary_key=True, index=True)
    user_id                       = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id                    = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    dropoff_time_hr               = Column(Float, nullable=False)   # hour vehicle is picked up by user
    pickup_time_hr                = Column(Float, nullable=False)   # hour vehicle is returned
    predicted_charging_energy_kwh = Column(Float, nullable=True)    # from Task 7 model
    created_at                    = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user    = relationship("User", back_populates="bookings")
    vehicle = relationship("Vehicle", back_populates="bookings")
