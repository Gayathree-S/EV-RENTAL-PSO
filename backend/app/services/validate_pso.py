"""
Validation script for pso_optimizer.py — Task 4 of 13.

Uses reduced swarm/iterations for fast demo output:
  - num_particles=10, max_iterations=30  (full paper run: 20 particles, 100 iters)
  - verbose=True to show iteration-by-iteration progress

Production usage:
    run_pso(N=2, min_evs=10, max_evs=100)              # uses default 20×100
    run_pso(N=10, min_evs=10, max_evs=100)             # uses default 20×100
"""

import sys
import os

# Ensure backend/ is on the path when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.pso_optimizer import run_pso


# ------------------------------------------------------------------
# Validation parameters (fast demo — increase for a real run)
# ------------------------------------------------------------------
DEMO_PARTICLES  = 10   # paper uses 20
DEMO_ITERATIONS = 30   # paper uses 100
# ------------------------------------------------------------------


def print_result(label: str, result: dict) -> None:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print("Best allocation:")
    for bus, evs in sorted(result["best_allocation"].items()):
        print(f"    Bus {bus:2d}: {evs} EVs")
    total_evs = sum(result["best_allocation"].values())
    print(f"  Total EVs placed : {total_evs}")
    print(f"  Best fitness     : {result['best_fitness']:.4f}")
    print(f"  Voltage violations: {result['num_violations']}")
    print("\nConvergence history (all iterations):")
    for i, f in enumerate(result["convergence_history"], start=1):
        print(f"    iter {i:3d}: {f:.4f}")


if __name__ == "__main__":
    print("=" * 60)
    print("  PSO Validation — EV Rental Centre Allocation")
    print(f"  Swarm size={DEMO_PARTICLES}, Iterations={DEMO_ITERATIONS}")
    print("  (Paper full run: 20 particles, 100 iterations)")
    print("=" * 60)

    # --- N=2 case (paper Table 3: expects buses close to {2:100, 4:100}, 0 violations) ---
    print("\n[N=2] Running PSO (verbose)...")
    r2 = run_pso(
        N=2,
        min_evs=10,
        max_evs=100,
        num_particles=DEMO_PARTICLES,
        max_iterations=DEMO_ITERATIONS,
        verbose=True,
    )
    print_result("N=2  (Paper baseline: buses {2:100, 4:100}, 0 violations)", r2)

    # --- N=10 case (paper Table 3: expects some buses below max due to voltage limits) ---
    print("\n[N=10] Running PSO (verbose)...")
    r10 = run_pso(
        N=10,
        min_evs=10,
        max_evs=100,
        num_particles=DEMO_PARTICLES,
        max_iterations=DEMO_ITERATIONS,
        verbose=True,
    )
    print_result("N=10 (Paper: some locations < max EVs when voltage binding)", r10)

    print("\nValidation complete.")
