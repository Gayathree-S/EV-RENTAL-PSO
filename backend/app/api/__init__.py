"""
API package initialization — exposes all routers.
"""

from app.api.auth import router as auth_router
from app.api.centers import router as centers_router
from app.api.bookings import router as bookings_router
from app.api.optimizer import router as optimizer_router

__all__ = ["auth_router", "centers_router", "bookings_router", "optimizer_router"]
