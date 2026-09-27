"""
Authentication API routes — Task 9.

NOTE: This is a simplified demo authentication flow designed for a final-year
academic demonstration. It performs direct hashed-password verification and returns
user identity details for frontend session storage without JWT tokens, refresh
mechanisms, or complex permission middlewares.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    # Check for duplicate email
    existing_user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Always create standard (non-admin) users via public registration
    new_user = User(
        name=req.name.strip(),
        email=req.email.strip().lower(),
        hashed_password=hash_password(req.password),
        is_admin=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="User login (returns user session info)",
)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return UserLoginResponse(
        user_id=user.id,
        name=user.name,
        email=user.email,
        is_admin=user.is_admin,
    )
