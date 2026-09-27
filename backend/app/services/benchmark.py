"""
PSO vs GA Benchmark — Task 6 of 13.

Runs both optimizers on N=2 and N=10 cases and saves results to
backend/data/benchmark_results.json for later use by the admin dashboard (Task 11).

Benchmark settings (lighter than full paper, chosen for fast demo-friendly run):
    PSO : num_particles=15, max_iterations=30
    GA  : population_size=15, generations=30
With the Part-A caching fix (~0.075s/call), each optimizer run finishes in ~1-3 min.
"""

import json
import time
from pathlib import Path

from app.services.pso_optimizer import run_pso
from app.services.ga_optimizer import run_ga

# Output file consumed by Task 11 admin dashboard
OUTPUT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "benchmark_results.json"

# -------------------------------------------------------------------
# Benchmark settings (documented: lighter than paper's 20×100 for speed)
# -------------------------------------------------------------------
PSO_PARTICLES  = 15
PSO_ITERATIONS = 30
GA_POPULATION  = 15
GA_GENERATIONS = 30
# -------------------------------------------------------------------

CASES = [
    {"label": "case_N2",  "N": 2,  "min_evs": 10, "max_evs": 100},
    {"label": "case_N10", "N": 10, "min_evs": 10, "max_evs": 100},
]


def run_timed_pso(N, min_evs, max_evs):
    print(f"    [PSO] N={N} starting...")
    t0 = time.time()
    result = run_pso(
        N=N, min_evs=min_evs, max_evs=max_evs,
        num_particles=PSO_PARTICLES,
        max_iterations=PSO_ITERATIONS,
        verbose=True,
    )
    elapsed = round(time.time() - t0, 2)
    return result, elapsed


def run_timed_ga(N, min_evs, max_evs):
    print(f"    [GA]  N={N} starting...")
    t0 = time.time()
    result = run_ga(
        N=N, min_evs=min_evs, max_evs=max_evs,
        population_size=GA_POPULATION,
        generations=GA_GENERATIONS,
        verbose=True,
    )
    elapsed = round(time.time() - t0, 2)
    return result, elapsed


def build_record(result: dict, elapsed: float) -> dict:
    return {
        "best_fitness":       result["best_fitness"],
        "best_allocation":    {str(k): v for k, v in result["best_allocation"].items()},
        "num_violations":     result["num_violations"],
        "convergence_history": result["convergence_history"],
        "time_seconds":       elapsed,
    }


def print_summary(rows: list) -> None:
    header = f"{'Case':<8} | {'Algorithm':<9} | {'Best Fitness':>14} | {'Violations':>10} | {'Time (s)':>9}"
    sep    = "-" * len(header)
    print(f"\n{sep}")
    print(header)
    print(sep)
    for row in rows:
        print(
            f"{row['case']:<8} | {row['algo']:<9} | {row['fitness']:>14.4f} | "
            f"{row['violations']:>10} | {row['time']:>9.2f}"
        )
    print(sep)


if __name__ == "__main__":
    print("=" * 65)
    print("  PSO vs GA Benchmark  (Task 6)")
    print(f"  PSO: {PSO_PARTICLES} particles × {PSO_ITERATIONS} iters")
    print(f"  GA : {GA_POPULATION} population × {GA_GENERATIONS} generations")
    print("=" * 65)

    benchmark_results = {}
    summary_rows = []

    for case in CASES:
        label   = case["label"]
        N       = case["N"]
        min_evs = case["min_evs"]
        max_evs = case["max_evs"]

        print(f"\n--- {label} (N={N}) ---")

        # PSO
        pso_result, pso_time = run_timed_pso(N, min_evs, max_evs)
        summary_rows.append({
            "case":       label, "algo": "PSO",
            "fitness":    pso_result["best_fitness"],
            "violations": pso_result["num_violations"],
            "time":       pso_time,
        })

        # GA
        ga_result, ga_time = run_timed_ga(N, min_evs, max_evs)
        summary_rows.append({
            "case":       label, "algo": "GA",
            "fitness":    ga_result["best_fitness"],
            "violations": ga_result["num_violations"],
            "time":       ga_time,
        })

        benchmark_results[label] = {
            "pso": build_record(pso_result, pso_time),
            "ga":  build_record(ga_result,  ga_time),
        }

    # Save JSON
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(benchmark_results, f, indent=2)
    print(f"\nResults saved -> {OUTPUT_PATH}")

    # Print summary table
    print_summary(summary_rows)
    print("\nBenchmark complete.")
