r"""
API Validation Script — Task 9 of 13.

Demonstrates and verifies:
  1. POST /auth/register — Register a new test user
  2. POST /auth/login — Authenticate the user and get session response
  3. GET /centers — Query all rental centers with nested fleet vehicles
  4. POST /bookings — Create a vehicle booking with ML-predicted charging energy
  5. GET /bookings — Retrieve bookings list (admin view, newest first)
  6. GET /optimizer/results — Fetch precomputed benchmark JSON results

Run from backend/ directory:
    ..\venv\Scripts\python.exe -m app.api.validate_api
or from project root:
    .\venv\Scripts\python.exe backend/app/api/validate_api.py
"""

import sys
import json
from pathlib import Path

# Ensure 'backend/' is in sys.path
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models import User, Vehicle, Booking


def run_api_validation():
    print("=" * 70)
    print("       FastAPI Endpoint Validation Suite (Task 9)")
    print("=" * 70)

    client = TestClient(app)

    # 0. Health check
    print("\n[0] GET /health")
    res = client.get("/health")
    print(f"Status: {res.status_code}, Response: {res.json()}")
    assert res.status_code == 200, "Health check failed"

    # 1. Register a new user (use timestamp/unique email if re-run)
    test_email = "testuser@example.com"
    # Clean up prior test user if needed
    db = SessionLocal()
    try:
        prior_user = db.query(User).filter(User.email == test_email).first()
        if prior_user:
            # delete old bookings for this user if any
            db.query(Booking).filter(Booking.user_id == prior_user.id).delete()
            db.delete(prior_user)
            db.commit()
    finally:
        db.close()

    print("\n[1] POST /auth/register")
    reg_payload = {
        "name": "Alex Tester",
        "email": test_email,
        "password": "Password123!",
    }
    res = client.post("/auth/register", json=reg_payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 201, f"Registration failed: {res.text}"
    user_data = res.json()
    user_id = user_data["id"]

    # 2. Login with the user
    print("\n[2] POST /auth/login")
    login_payload = {
        "email": test_email,
        "password": "Password123!",
    }
    res = client.post("/auth/login", json=login_payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 200, f"Login failed: {res.text}"
    login_data = res.json()
    assert login_data["user_id"] == user_id

    # 3. GET /centers
    print("\n[3] GET /centers")
    res = client.get("/centers")
    print(f"Status: {res.status_code}")
    centers = res.json()
    print(f"Total Centers Returned: {len(centers)}")
    print(f"First Center: {centers[0]['name']} (Bus {centers[0]['bus_number']}), Max Fleet: {centers[0]['max_fleet_size']}")
    print(f"Vehicles in First Center: {len(centers[0]['vehicles'])}")
    for v in centers[0]["vehicles"][:3]:
        print(f"  - Vehicle ID {v['id']}: Code={v['vehicle_code']}, Available={v['is_available']}")
    assert res.status_code == 200 and len(centers) > 0

    # Pick an available vehicle
    target_vehicle_id = None
    target_vehicle_code = None
    for c in centers:
        for v in c["vehicles"]:
            if v["is_available"]:
                target_vehicle_id = v["id"]
                target_vehicle_code = v["vehicle_code"]
                break
        if target_vehicle_id is not None:
            break

    assert target_vehicle_id is not None, "No available vehicle found for testing booking"

    # 4. POST /bookings
    print(f"\n[4] POST /bookings (Booking Vehicle '{target_vehicle_code}' for User ID {user_id})")
    booking_payload = {
        "user_id": user_id,
        "vehicle_id": target_vehicle_id,
        "dropoff_time_hr": 9.0,   # 09:00 AM
        "pickup_time_hr": 17.5,   # 05:30 PM (8.5 hr duration)
    }
    res = client.post("/bookings", json=booking_payload)
    print(f"Status: {res.status_code}")
    booking_res = res.json()
    print(f"Response: {json.dumps(booking_res, indent=2)}")
    assert res.status_code == 201, f"Booking creation failed: {res.text}"
    assert booking_res["predicted_charging_energy_kwh"] is not None
    print(f"--> ML Predicted Charging Energy: {booking_res['predicted_charging_energy_kwh']:.2f} kWh")

    # 5. GET /bookings (Admin view & User view)
    print("\n[5a] GET /bookings (All Bookings)")
    res = client.get("/bookings")
    print(f"Status: {res.status_code}")
    all_bookings = res.json()
    print(f"Total Bookings Count: {len(all_bookings)}")
    latest = all_bookings[0]
    print(f"Latest Booking ID: {latest['id']}, User: {latest['user']['name']} ({latest['user']['email']}), Vehicle: {latest['vehicle']['vehicle_code']}, Predicted Energy: {latest['predicted_charging_energy_kwh']} kWh")

    print(f"\n[5b] GET /bookings/user/{user_id} (User Specific Bookings)")
    res = client.get(f"/bookings/user/{user_id}")
    print(f"Status: {res.status_code}")
    user_bookings = res.json()
    print(f"User Bookings Count: {len(user_bookings)}")
    assert len(user_bookings) >= 1

    # 6. GET /optimizer/results
    print("\n[6] GET /optimizer/results")
    res = client.get("/optimizer/results")
    print(f"Status: {res.status_code}")
    bench_data = res.json()
    print(f"Benchmark Cases Present: {list(bench_data.keys())}")
    print(f"Case N=2 PSO Best Fitness: {bench_data['case_N2']['pso']['best_fitness']}")
    print(f"Case N=10 PSO Best Fitness: {bench_data['case_N10']['pso']['best_fitness']}")
    assert "case_N2" in bench_data and "case_N10" in bench_data

    # 7. Error cases validation
    print("\n[7] Error Handling Validation:")
    # 7a. Duplicate registration
    dup_res = client.post("/auth/register", json=reg_payload)
    print(f"  - Duplicate register status: {dup_res.status_code} ({dup_res.json()['detail']})")
    assert dup_res.status_code == 400

    # 7b. Invalid login password
    bad_login_res = client.post("/auth/login", json={"email": test_email, "password": "wrongpassword"})
    print(f"  - Bad password login status: {bad_login_res.status_code} ({bad_login_res.json()['detail']})")
    assert bad_login_res.status_code == 401

    # 7c. Double booking unavailable vehicle
    dup_booking_res = client.post("/bookings", json=booking_payload)
    print(f"  - Unavailable vehicle booking status: {dup_booking_res.status_code} ({dup_booking_res.json()['detail']})")
    assert dup_booking_res.status_code == 400

    print("\n" + "=" * 70)
    print("       ALL API ENDPOINT VALIDATION CHECKS PASSED (Task 9)")
    print("=" * 70)


if __name__ == "__main__":
    run_api_validation()
