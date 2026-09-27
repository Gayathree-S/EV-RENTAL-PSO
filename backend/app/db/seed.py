r"""
Seed script — Task 8 of 13.

Creates all tables and populates them with demo data:
  - RentalCenter rows sourced from PSO N=10 best_allocation in benchmark_results.json
  - min(5, max_fleet_size) Vehicle rows per center
  - 2 demo Users (regular + admin), password: demo1234

Run from backend/ directory:
    ..\venv\Scripts\python.exe -m app.db.seed
"""

import json
import sys
from pathlib import Path

# Ensure 'backend/' is importable when run as __main__
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from passlib.context import CryptContext

# Import all models to register them with Base.metadata
from app.models import User, RentalCenter, Vehicle, Booking  # noqa: F401
from app.db.session import Base, engine, SessionLocal

BENCHMARK_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "benchmark_results.json"

DEMO_PASSWORD   = "demo1234"
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)


def run_seed() -> None:
    print("=" * 60)
    print("  Database Seed Script — Task 8")
    print("=" * 60)

    # 1. Create all tables
    print("\nCreating tables...")
    Base.metadata.create_all(bind=engine)
    print("  Tables created: users, rental_centers, vehicles, bookings")

    db = SessionLocal()
    try:
        # ------------------------------------------------------------------
        # Guard: skip if already seeded
        # ------------------------------------------------------------------
        if db.query(RentalCenter).count() > 0:
            print("\nDatabase already seeded — skipping. Delete app.db to re-seed.")
            return

        # ------------------------------------------------------------------
        # 2. Load PSO N=10 best_allocation from Task 6 benchmark results
        # ------------------------------------------------------------------
        with open(BENCHMARK_PATH, "r") as f:
            benchmark = json.load(f)

        pso_n10_allocation: dict = benchmark["case_N10"]["pso"]["best_allocation"]
        print(f"\nLoaded PSO N=10 allocation ({len(pso_n10_allocation)} centers) from benchmark_results.json")

        # ------------------------------------------------------------------
        # 3. Create RentalCenter + Vehicle rows
        # ------------------------------------------------------------------
        centers_created = 0
        vehicles_created = 0

        for bus_str, max_fleet in pso_n10_allocation.items():
            bus_num = int(bus_str)
            center = RentalCenter(
                bus_number=bus_num,
                name=f"Center at Bus {bus_num}",
                max_fleet_size=max_fleet,
            )
            db.add(center)
            db.flush()  # get center.id before creating vehicles

            num_vehicles = min(5, max_fleet)
            for n in range(1, num_vehicles + 1):
                vehicle = Vehicle(
                    center_id=center.id,
                    vehicle_code=f"EV-{center.id}-{n:02d}",
                    is_available=True,
                )
                db.add(vehicle)
                vehicles_created += 1

            centers_created += 1

        # ------------------------------------------------------------------
        # 4. Create 2 demo users
        # ------------------------------------------------------------------
        users = [
            User(
                name="Demo User",
                email="user@demo.com",
                hashed_password=hash_password(DEMO_PASSWORD),
                is_admin=False,
            ),
            User(
                name="Demo Admin",
                email="admin@demo.com",
                hashed_password=hash_password(DEMO_PASSWORD),
                is_admin=True,
            ),
        ]
        for u in users:
            db.add(u)

        db.commit()

        # ------------------------------------------------------------------
        # 5. Print summary
        # ------------------------------------------------------------------
        print(f"\nSeed complete!")
        print(f"  Rental Centers : {centers_created}")
        print(f"  Vehicles       : {vehicles_created}")
        print(f"  Users          : {len(users)}")
        print(f"\nDemo credentials (password for both: '{DEMO_PASSWORD}'):")
        print(f"  Regular user : user@demo.com")
        print(f"  Admin        : admin@demo.com")
        print(f"\n  NOTE: These are demo-only credentials. Change before any real deployment.")

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
