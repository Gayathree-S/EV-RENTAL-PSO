r"""
Database validation script — Task 8 of 13.

Queries and prints:
  - All rental centers with their allocated max_fleet_size and actual seeded vehicle counts.
  - All registered users (email and is_admin flag only — NEVER prints password hashes).

Run from backend/ directory:
    ..\venv\Scripts\python.exe -m app.db.validate_db
or from project root:
    .\venv\Scripts\python.exe backend/app/db/validate_db.py
"""

import sys
from pathlib import Path

# Ensure 'backend/' is in sys.path
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.db.session import SessionLocal
from app.models import RentalCenter, Vehicle, User, Booking  # noqa: F401


def validate_database() -> None:
    print("=" * 65)
    print("       Database Validation Report (Task 8 — SQLite Schema)")
    print("=" * 65)

    db = SessionLocal()
    try:
        # 1. Query Users
        users = db.query(User).all()
        print(f"\n[1] Users ({len(users)} registered):")
        print("-" * 55)
        print(f"  {'ID':<5} {'Email':<25} {'Role':<12} {'Created At'}")
        print("-" * 55)
        for u in users:
            role = "Admin" if u.is_admin else "Regular"
            created = u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else "N/A"
            print(f"  {u.id:<5} {u.email:<25} {role:<12} {created}")

        # 2. Query Rental Centers & Vehicle Counts
        centers = db.query(RentalCenter).order_by(RentalCenter.id).all()
        total_vehicles = db.query(Vehicle).count()
        print(f"\n[2] Rental Centers ({len(centers)} centers, {total_vehicles} total vehicles):")
        print("-" * 65)
        print(f"  {'ID':<4} {'Bus':<6} {'Name':<22} {'Max Fleet':<12} {'Seeded EVs'}")
        print("-" * 65)
        for c in centers:
            seeded_count = len(c.vehicles)
            print(f"  {c.id:<4} {c.bus_number:<6} {c.name:<22} {c.max_fleet_size:<12} {seeded_count}")

        # 3. Sample Vehicles display
        sample_vehicles = db.query(Vehicle).limit(6).all()
        print(f"\n[3] Sample Vehicles (showing first {len(sample_vehicles)} of {total_vehicles}):")
        print("-" * 55)
        print(f"  {'ID':<5} {'Code':<15} {'Center ID':<12} {'Available'}")
        print("-" * 55)
        for v in sample_vehicles:
            print(f"  {v.id:<5} {v.vehicle_code:<15} {v.center_id:<12} {v.is_available}")

        # 4. Summary counts
        booking_count = db.query(Booking).count()
        print("\n" + "=" * 65)
        print(f"Summary: {len(centers)} centers, {total_vehicles} vehicles, {len(users)} users, {booking_count} bookings.")
        print("=" * 65)

    finally:
        db.close()


if __name__ == "__main__":
    validate_database()
