from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id           = Column(Integer, primary_key=True, index=True)
    center_id    = Column(Integer, ForeignKey("rental_centers.id"), nullable=False)
    vehicle_code = Column(String, unique=True, nullable=False)  # e.g. "EV-001"
    is_available = Column(Boolean, default=True, nullable=False)

    # Relationships
    center   = relationship("RentalCenter", back_populates="vehicles")
    bookings = relationship("Booking", back_populates="vehicle")
