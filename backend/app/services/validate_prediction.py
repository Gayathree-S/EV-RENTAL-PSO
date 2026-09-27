"""
Validation script for prediction_model.py — Task 7 of 13.
Trains the model, prints metrics, and sanity-checks predictions on 3 sample bookings.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.prediction_model import train_and_save, predict_charging_energy

if __name__ == "__main__":
    print("=" * 60)
    print("  Charging Demand Prediction — Validation (Task 7)")
    print("=" * 60)

    # --- Train and evaluate ---
    print("\nTraining RandomForestRegressor (n_estimators=100, random_state=42)...")
    metrics = train_and_save()

    print(f"\nDataset split: {metrics['n_train']} train / {metrics['n_test']} test (80/20)")
    print(f"  Train MAE : {metrics['mae_train']:.4f} kWh")
    print(f"  Train R2  : {metrics['r2_train']:.4f}")
    print(f"  Test  MAE : {metrics['mae_test']:.4f} kWh")
    print(f"  Test  R2  : {metrics['r2_test']:.4f}")
    print(
        "\n  Note: With only 140 rows of noisy real-world renter data, a moderate R2\n"
        "  is expected and acceptable. This is a demo integration feature, not a\n"
        "  research contribution. MAE gives the more interpretable error in kWh."
    )

    print("\nModel saved to backend/data/charging_prediction_model.pkl")

    # --- Sample predictions ---
    print("\n" + "=" * 60)
    print("  Sample Predictions")
    print("=" * 60)

    samples = [
        ("Short daytime rental",  9.0,  13.0,  "09:00 drop -> 13:00 pickup (4h)"),
        ("Typical evening rental", 18.0, 22.0, "18:00 drop -> 22:00 pickup (4h)"),
        ("Overnight rental",       22.0,  8.0, "22:00 drop -> 08:00 pickup (10h)"),
    ]

    for label, dropoff, pickup, desc in samples:
        pred = predict_charging_energy(dropoff, pickup)
        print(f"  {label}")
        print(f"    Input  : {desc}")
        print(f"    Predicted charging energy: {pred:.2f} kWh")
        print()

    print("Expected range from dataset: ~10-112 kWh")
    print("\nValidation complete.")
