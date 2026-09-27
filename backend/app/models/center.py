from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base


class RentalCenter(Base):
    __tablename__ = "rental_centers"

    id            = Column(Integer, primary_key=True, index=True)
    bus_number    = Column(Integer, nullable=False)          # grid bus from PSO/GA output
    name          = Column(String, nullable=False)           # e.g. "Center at Bus 2"
    max_fleet_size = Column(Integer, nullable=False)         # allocated EV count for this bus

    # Relationships
    vehicles = relationship("Vehicle", back_populates="center")
