"""
FastAPI application entrypoint.
Configures CORS middleware and registers all API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.centers import router as centers_router
from app.api.bookings import router as bookings_router
from app.api.optimizer import router as optimizer_router

app = FastAPI(
    title="AI-Powered Smart EV Rental Management System API",
    description="Backend API for EV Rental Management, Fleet Optimization, Demand Forecasting, and Analytics",
    version="1.0.0",
)

# CORS middleware for Next.js frontend (default port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(centers_router)
app.include_router(bookings_router)
app.include_router(optimizer_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
