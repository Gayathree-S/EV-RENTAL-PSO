"""
Charging Demand Prediction Model — Task 7 of 13.

Predicts how much charging energy (kWh) an EV booking will require based on
renter behaviour patterns in the base-paper dataset.

SCOPE NOTE:
    This model predicts CHARGING DEMAND (energy consumed during a rental session),
    NOT battery health or degradation.  The dataset (ev_renter_behavior.csv) contains
    only charging_energy_kwh, dropoff_time_hr, and pickup_time_hr — it does not include
    battery state-of-charge, cycle count, temperature, or any degradation-related
    signal.  Claiming degradation prediction from this data would be scientifically
    unsound.

Features used (known at booking time):
    dropoff_time_hr  — hour of day the vehicle is dropped off for charging [0, 24)
    duration_hours   — scheduled rental duration derived from pickup and dropoff times
                       (wraparound logic for overnight sessions matches load_profile.py)

Target:
    charging_energy_kwh — total energy consumed during the session (kWh)

Model:
    RandomForestRegressor (scikit-learn), n_estimators=100, random_state=42.
    With only 140 rows of noisy real-world renter data, a high R2 is not expected
    and not the goal — this is a demo feature showing ML integration, not a research
    contribution.  Actual MAE and R2 are reported as-is without cherry-picking.
"""

import os
from pathlib import Path
from typing import Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_SERVICES_DIR = Path(__file__).resolve().parent
_DATA_DIR     = _SERVICES_DIR.parent.parent / "data"
_CSV_PATH     = _DATA_DIR / "ev_renter_behavior.csv"
_MODEL_PATH   = _DATA_DIR / "charging_prediction_model.pkl"

# ---------------------------------------------------------------------------
# In-memory model cache (loaded once, reused on every predict call)
# ---------------------------------------------------------------------------
_MODEL_CACHE: Optional[RandomForestRegressor] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_duration(dropoff: float, pickup: float) -> float:
    """Compute session duration in hours, handling overnight wraparound.

    Wraparound logic is identical to load_profile.py:
        if pickup <= dropoff -> session crosses midnight
    """
    if pickup <= dropoff:
        duration = (24.0 - dropoff) + pickup
    else:
        duration = pickup - dropoff
    return max(duration, 0.25)   # floor at 15 min to avoid zero-duration edge cases


def _load_features() -> Tuple[pd.DataFrame, pd.Series]:
    """Load CSV and engineer features.  Returns (X, y)."""
    df = pd.read_csv(_CSV_PATH)

    df["duration_hours"] = df.apply(
        lambda row: _compute_duration(row["dropoff_time_hr"], row["pickup_time_hr"]),
        axis=1,
    )

    X = df[["dropoff_time_hr", "duration_hours"]]
    y = df["charging_energy_kwh"]
    return X, y


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_and_save(
    random_state: int = 42,
    test_size: float = 0.20,
    n_estimators: int = 100,
) -> dict:
    """Train RandomForestRegressor and save model to disk.

    Returns
    -------
    dict  {mae_train, r2_train, mae_test, r2_test}
    """
    X, y = _load_features()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=random_state,
    )
    model.fit(X_train, y_train)

    # Evaluate on both splits
    y_pred_train = model.predict(X_train)
    y_pred_test  = model.predict(X_test)

    metrics = {
        "mae_train": float(mean_absolute_error(y_train, y_pred_train)),
        "r2_train":  float(r2_score(y_train, y_pred_train)),
        "mae_test":  float(mean_absolute_error(y_test, y_pred_test)),
        "r2_test":   float(r2_score(y_test, y_pred_test)),
        "n_train":   len(X_train),
        "n_test":    len(X_test),
    }

    # Save model
    _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, _MODEL_PATH)

    # Update in-memory cache so the same process can predict without re-loading
    global _MODEL_CACHE
    _MODEL_CACHE = model

    return metrics


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def _get_model() -> RandomForestRegressor:
    """Return cached model, loading from disk on first call."""
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {_MODEL_PATH}. "
                "Run train_and_save() first."
            )
        _MODEL_CACHE = joblib.load(_MODEL_PATH)
    return _MODEL_CACHE


def predict_charging_energy(dropoff_time_hr: float, pickup_time_hr: float) -> float:
    """Predict charging energy (kWh) for a rental booking.

    Parameters
    ----------
    dropoff_time_hr : float
        Hour of day the EV is dropped off [0, 24).
    pickup_time_hr : float
        Hour of day the EV will be picked up [0, 24).

    Returns
    -------
    float
        Predicted charging energy in kWh.  Roughly in the range of the training
        dataset (~10-112 kWh); clamped to [0, 200] as a safety floor/ceiling.
    """
    duration = _compute_duration(dropoff_time_hr, pickup_time_hr)
    features = pd.DataFrame(
        [[dropoff_time_hr, duration]],
        columns=["dropoff_time_hr", "duration_hours"],
    )
    model = _get_model()
    prediction = float(model.predict(features)[0])
    return round(max(0.0, min(prediction, 200.0)), 2)
