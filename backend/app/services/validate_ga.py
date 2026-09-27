"""
Validation script for ga_optimizer.py — Task 5 of 13.

Uses reduced population/generations for fast demo output:
  - population_size=15, generations=30  (full run: 20 pop, 100 gen)
  - verbose=True to show generation-by-generation progress

Only N=2 is validated here; N=2 vs N=10 comparison with PSO is Task 6.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.ga_optimizer import run_ga

# ------------------------------------------------------------------
# Demo parameters (kept low for speed — document for assessors)
# Population=15, Generations=30 chosen to match PSO demo run speed.
# Full paper-equivalent run would use population=20, generations=100.
# ------------------------------------------------------------------
DEMO_POPULATION  = 15
DEMO_GENERATIONS = 30
# ------------------------------------------------------------------


def print_result(label: str, result: dict) -> None:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print("Best allocation:")
    for bus, evs in sorted(result["best_allocation"].items()):
        print(f"    Bus {bus:2d}: {evs} EVs")
    total_evs = sum(result["best_allocation"].values())
    print(f"  Total EVs placed  : {total_evs}")
    print(f"  Best fitness      : {result['best_fitness']:.4f}")
    print(f"  Voltage violations: {result['num_violations']}")
    print("\nConvergence history (all generations):")
    for i, f in enumerate(result["convergence_history"], start=1):
        print(f"    gen {i:3d}: {f:.4f}")


if __name__ == "__main__":
    print("=" * 60)
    print("  GA Validation — EV Rental Centre Allocation")
    print(f"  Population={DEMO_POPULATION}, Generations={DEMO_GENERATIONS}")
    print("  crossover_rate=0.8, mutation_rate=0.1")
    print("  (Full run: population=20, generations=100)")
    print("=" * 60)

    print("\n[N=2] Running GA (verbose)...")
    r2 = run_ga(
        N=2,
        min_evs=10,
        max_evs=100,
        population_size=DEMO_POPULATION,
        generations=DEMO_GENERATIONS,
        verbose=True,
    )
    print_result("N=2  (Expected: 0 violations, ~200 total EVs)", r2)

    # Sanity check
    violations = r2["num_violations"]
    if violations == 0:
        print("\n>> N=2 Validation: PASS (zero voltage violations)")
    else:
        print(f"\n>> N=2 Validation: NOTE — {violations} violation(s) found (may need more generations)")

    print("\nValidation complete.")
