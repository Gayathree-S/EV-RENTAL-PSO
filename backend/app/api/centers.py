"""
Rental Centers and Fleet Inventory API routes — Task 9.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.center import RentalCenter
from app.schemas.center import RentalCenterOut

router = APIRouter(prefix="/centers", tags=["Rental Centers"])


@router.get(
    "",
    response_model=List[RentalCenterOut],
    summary="Get all rental centers with their fleet vehicles",
)
def get_all_centers(db: Session = Depends(get_db)):
    centers = db.query(RentalCenter).order_by(RentalCenter.id).all()
    return centers


@router.get(
    "/{center_id}",
    response_model=RentalCenterOut,
    summary="Get a single rental center by ID with its vehicles",
)
def get_center_by_id(center_id: int, db: Session = Depends(get_db)):
    center = db.query(RentalCenter).filter(RentalCenter.id == center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental center with ID {center_id} not found",
        )
    return center
