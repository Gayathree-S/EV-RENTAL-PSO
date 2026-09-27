"""
Power Flow and Scenario Evaluation Validation Script.

Validates:
1. Baseline power flow (0 EVs) - voltages within [0.95, 1.05] p.u., zero violations.
2. Sample N=2 allocation {2: 100, 4: 100} - valid voltages within bounds.
3. Overloaded test case {2: 500, 18: 150} - verifies voltage violation detection with AC convergence.
4. Extreme stress test {18: 5000} - verifies graceful non-convergence penalty handling.
"""

import sys
import os
from pathlib import Path

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.load_profile import compute_ev_load_profile
from app.services.power_flow import evaluate_scenario


def run_validation():
    print("=" * 70)
    print("POWER-SYSTEM & POWER-FLOW MODULE VALIDATION (IEEE 33-BUS + 3.6 MW DG)")
    print("=" * 70)

    # 1. Per-unit EV load profile computation
    print("\n--- STEP 1: EV Per-Unit Demand Computation ---")
    hourly_loads, per_unit_kw = compute_ev_load_profile()
    print(f"Peak fleet load at 20:00 : {hourly_loads.max():.2f} kW")
    print(f"Per-unit peak demand     : {per_unit_kw:.4f} kW/EV ({per_unit_kw / 1000.0:.6f} MW/EV)")

    # 2. Baseline Scenario (No EVs)
    print("\n--- STEP 2: Baseline Scenario (0 EVs Allocated) ---")
    baseline_res = evaluate_scenario(ev_allocation={}, per_unit_kw_per_ev=per_unit_kw)
    print(f"Total Active Losses: {baseline_res['total_active_loss_mw']:.4f} MW ({baseline_res['total_active_loss_mw'] * 1000:.2f} kW)")
    print(f"Number of Voltage Violations: {baseline_res['num_violations']}")
    print(f"Violating Buses: {baseline_res['voltage_violations']}")
    print("Bus Voltages (p.u.):")
    for b in range(1, 34):
        v = baseline_res["bus_voltages"][b]
        status = "OK" if 0.95 <= v <= 1.05 else "VIOLATION"
        print(f"  Bus {b:02d}: {v:.4f} p.u. [{status}]", end="\n" if b % 3 == 0 or b == 33 else " | ")

    assert baseline_res["num_violations"] == 0, "Baseline scenario should have 0 violations!"
    print("\n>> Baseline validation: PASS (All voltages inside [0.95, 1.05] p.u.)")

    # 3. Paper Sample Allocation (N=2 case: {2: 100, 4: 100})
    print("\n--- STEP 3: Sample N=2 Allocation ({Bus 2: 100 EVs, Bus 4: 100 EVs}) ---")
    alloc_n2 = {2: 100, 4: 100}
    n2_res = evaluate_scenario(ev_allocation=alloc_n2, per_unit_kw_per_ev=per_unit_kw)
    print(f"Total Active Losses: {n2_res['total_active_loss_mw']:.4f} MW ({n2_res['total_active_loss_mw'] * 1000:.2f} kW)")
    print(f"Number of Voltage Violations: {n2_res['num_violations']}")
    print(f"Violating Buses: {n2_res['voltage_violations']}")
    print("Key Bus Voltages:")
    for b in [1, 2, 4, 6, 18, 33]:
        v = n2_res["bus_voltages"][b]
        print(f"  Bus {b:02d}: {v:.4f} p.u.")

    assert n2_res["num_violations"] == 0, "N=2 scenario {2: 100, 4: 100} should have 0 violations!"
    print(">> Sample N=2 allocation validation: PASS (Zero violations, matched bounds)")

    # 4. Overloaded Scenario ({2: 500, 18: 150})
    print("\n--- STEP 4: Overloaded Stress Test ({Bus 2: 500 EVs, Bus 18: 150 EVs}) ---")
    alloc_overload = {2: 500, 18: 150}
    overload_res = evaluate_scenario(ev_allocation=alloc_overload, per_unit_kw_per_ev=per_unit_kw)
    print(f"Total Active Losses: {overload_res['total_active_loss_mw']:.4f} MW ({overload_res['total_active_loss_mw'] * 1000:.2f} kW)")
    print(f"Number of Voltage Violations: {overload_res['num_violations']}")
    print(f"Violating Buses: {overload_res['voltage_violations']}")
    print("Violating Bus Voltages:")
    for b in overload_res["voltage_violations"]:
        v = overload_res["bus_voltages"][b]
        print(f"  Bus {b:02d}: {v:.4f} p.u. (Under-voltage < 0.95 p.u.)")

    assert overload_res["num_violations"] > 0, "Overloaded scenario should trigger voltage violations!"
    print(">> Overloaded stress test validation: PASS (Voltage violations detected accurately)")

    # 5. Extreme Non-Convergence Test
    print("\n--- STEP 5: Non-Convergence Graceful Penalty Test ({Bus 18: 5000 EVs}) ---")
    extreme_res = evaluate_scenario(ev_allocation={18: 5000}, per_unit_kw_per_ev=per_unit_kw)
    print(f"Non-convergence handled: num_violations = {extreme_res['num_violations']} (penalty value)")
    print(f"bus_voltages is None: {extreme_res['bus_voltages'] is None}")
    print(f"total_active_loss_mw is None: {extreme_res['total_active_loss_mw'] is None}")
    assert extreme_res["num_violations"] == 999, "Non-convergence should return penalty num_violations=999"
    print(">> Non-convergence fallback test: PASS (Returned penalty structure without crashing)")

    print("\n" + "=" * 70)
    print("[SUCCESS] All Power Flow & Network evaluation tests passed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    run_validation()
