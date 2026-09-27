"""
EV Renter Charging Load Profile and Per-Unit Demand Computation.

MODELING ASSUMPTION & METHODOLOGY NOTE:
----------------------------------------
The base research paper specifies that a "per-unit profile... considering the
highest magnitude of load during a day" is used to model EV charging demand added
to distribution buses. Because the paper does not publish an exact closed-form
derivation formula for this per-unit metric, this module implements a reasonable,
explicitly stated engineering approximation:

1. Each of the 140 empirical renter trips (from ev_renter_behavior.csv) is assigned
   a charging session active from its dropoff_time_hr until its pickup_time_hr
   (wrapping into the next day when pickup_time_hr <= dropoff_time_hr).
2. Constant charging power is assumed throughout each vehicle's connection window:
   P_ev (kW) = charging_energy_kwh / duration_hours.
3. For each hour h in [0..23], total charging demand (kW) is summed across all
   EVs active during that hour, generating a 24-hour aggregate load profile.
4. The peak aggregate load across the 24 hours is divided by the total number of
   vehicles (140) to determine the per-unit peak demand per EV (kW/EV):
   per_unit_kw_per_ev = max(hourly_total_load_kw) / 140.
"""

import os
from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd


def get_default_dataset_path() -> str:
    """Resolve absolute path to ev_renter_behavior.csv."""
    current_dir = Path(__file__).resolve().parent
    # services -> app -> backend -> data
    data_path = current_dir.parent.parent / "data" / "ev_renter_behavior.csv"
    return str(data_path)


def compute_ev_load_profile(csv_path: str = None) -> Tuple[np.ndarray, float]:
    """
    Computes the 24-hour aggregate EV charging load profile (in kW)
    and the corresponding peak per-unit charging demand per vehicle (in kW/EV).

    Parameters
    ----------
    csv_path : str, optional
        Path to ev_renter_behavior.csv. If None, uses default data path.

    Returns
    -------
    hourly_loads_kw : np.ndarray
        Array of length 24 containing total fleet charging demand in kW for hours 0..23.
    per_unit_kw_per_ev : float
        Peak hourly charging demand divided by total number of EVs (140).
    """
    if csv_path is None:
        csv_path = get_default_dataset_path()

    df = pd.read_csv(csv_path)
    num_evs = len(df)

    hourly_loads_kw = np.zeros(24, dtype=float)

    for _, row in df.iterrows():
        energy_kwh = float(row["charging_energy_kwh"])
        dropoff = float(row["dropoff_time_hr"])
        pickup = float(row["pickup_time_hr"])

        # Calculate session duration
        if pickup <= dropoff:
            duration = (24.0 - dropoff) + pickup
        else:
            duration = pickup - dropoff

        # Handle potential zero duration edge-case
        if duration <= 0:
            duration = 24.0

        charging_power_kw = energy_kwh / duration

        # Accumulate power for active hours
        for h in range(24):
            is_active = False
            if pickup <= dropoff:
                # Crosses midnight: active from dropoff through 23 and 0 up to pickup
                if h >= dropoff or h < pickup:
                    is_active = True
            else:
                # Same-day interval: active from dropoff up to pickup
                if dropoff <= h < pickup:
                    is_active = True

            if is_active:
                hourly_loads_kw[h] += charging_power_kw

    peak_load_kw = float(np.max(hourly_loads_kw))
    per_unit_kw_per_ev = peak_load_kw / float(num_evs)

    return hourly_loads_kw, per_unit_kw_per_ev


if __name__ == "__main__":
    hourly_profile, pu_kw_per_ev = compute_ev_load_profile()
    print("=" * 60)
    print("EV FLEET 24-HOUR AGGREGATE CHARGING LOAD PROFILE")
    print("=" * 60)
    for hr, load in enumerate(hourly_profile):
        bar = "#" * int(load / 25)
        print(f"Hour {hr:02d}:00 -> {load:8.2f} kW  {bar}")
    print("=" * 60)
    print(f"Peak Hourly Aggregate Load : {np.max(hourly_profile):8.2f} kW (at Hour {np.argmax(hourly_profile):02d}:00)")
    print(f"Minimum Hourly Load        : {np.min(hourly_profile):8.2f} kW (at Hour {np.argmin(hourly_profile):02d}:00)")
    print(f"Total Fleet Size           : 140 EVs")
    print(f"Per-Unit Peak Demand per EV: {pu_kw_per_ev:8.4f} kW/EV ({pu_kw_per_ev / 1000.0:8.6f} MW/EV)")
    print("=" * 60)
