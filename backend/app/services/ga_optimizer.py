"""
Genetic Algorithm (GA) optimizer for EV Rental Centre allocation.

Design decision:
    Reuses `decode_particle()` and `fitness_function()` directly from
    pso_optimizer.py — a chromosome is IDENTICAL in encoding to a PSO
    particle (vector of length 2*N: N location scores + N fleet sizes),
    decoded the same way.  This ensures the PSO vs GA comparison in Task 6
    is fair — same search space, same fitness landscape, different search
    strategy.

GA is intentionally kept simple (standard operators) for demo-level comparison:
    - Tournament selection (k=2)
    - Single-point crossover
    - Gaussian mutation per gene
    - Single-individual elitism
"""

import numpy as np
from typing import List, Dict, Any, Optional

from app.services.load_profile import compute_ev_load_profile
from app.services.power_flow import evaluate_scenario
from app.services.pso_optimizer import decode_particle, fitness_function


def run_ga(
    N: int,
    min_evs: int,
    max_evs: int,
    population_size: int = 20,
    generations: int = 100,
    mutation_rate: float = 0.1,
    crossover_rate: float = 0.8,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Run a Genetic Algorithm to optimise EV-rental-centre placement.

    Chromosome encoding
    -------------------
    Identical to PSO particle encoding (see pso_optimizer.decode_particle):
        chromosome[:N]  — location scores in [0, 1]
        chromosome[N:]  — fleet sizes in [min_evs, max_evs]

    GA operators
    ------------
    Selection  : binary tournament (k=2) — pick 2 random individuals, keep fitter
    Crossover  : single-point crossover, applied with probability crossover_rate
    Mutation   : per-gene Gaussian noise (σ = 0.1 × gene range), applied with
                 probability mutation_rate per gene
    Elitism    : top-1 individual carried unchanged into next generation

    Parameters
    ----------
    N              : number of rental centre locations
    min_evs        : minimum EVs per centre
    max_evs        : maximum EVs per centre
    population_size: number of chromosomes (default 20)
    generations    : number of GA generations (default 100)
    mutation_rate  : per-gene mutation probability (default 0.1)
    crossover_rate : crossover probability per pair (default 0.8)
    verbose        : if True, print best fitness after every generation

    Returns
    -------
    dict with keys matching run_pso() output for easy comparison:
        best_allocation    : {bus: num_evs}
        best_fitness       : float
        convergence_history: [float] — best fitness recorded each generation
        final_voltages     : {bus: voltage_pu} or None
        num_violations     : int
    """
    valid_buses: List[int] = list(range(2, 34))  # buses 2–33
    dim = 2 * N

    # Pre-compute EV load profile once
    _, per_unit_kw_per_ev = compute_ev_load_profile()

    rng = np.random.default_rng()

    # -----------------------------------------------------------------------
    # Initialise population (same bounds as PSO for fair comparison)
    # -----------------------------------------------------------------------
    population = np.empty((population_size, dim))
    population[:, :N] = rng.random((population_size, N))          # location scores [0,1]
    population[:, N:] = (
        min_evs + rng.random((population_size, N)) * (max_evs - min_evs)
    )                                                               # fleet sizes

    best_chromosome: Optional[np.ndarray] = None
    best_fitness: float = np.inf
    convergence_history: List[float] = []

    # -----------------------------------------------------------------------
    # Main GA loop
    # -----------------------------------------------------------------------
    for gen in range(generations):
        # --- Evaluate fitness for all chromosomes ---
        fitnesses = np.empty(population_size)
        for i in range(population_size):
            alloc = decode_particle(population[i], N, valid_buses, min_evs, max_evs)
            fitnesses[i] = fitness_function(alloc, per_unit_kw_per_ev=per_unit_kw_per_ev)

        # --- Update global best (elitism source) ---
        gen_best_idx = int(np.argmin(fitnesses))
        if fitnesses[gen_best_idx] < best_fitness:
            best_fitness = float(fitnesses[gen_best_idx])
            best_chromosome = population[gen_best_idx].copy()

        convergence_history.append(best_fitness)

        if verbose:
            print(f"  Gen {gen+1:4d}/{generations}  best_fitness={best_fitness:.4f}")

        # --- Build new population ---
        new_population = np.empty_like(population)

        # Elitism: slot 0 always gets the best chromosome seen so far
        new_population[0] = best_chromosome.copy()

        # Fill remaining slots with tournament → crossover → mutation
        for child_idx in range(1, population_size):
            # Tournament selection for parent A
            a1, a2 = rng.integers(0, population_size, size=2)
            parent_a = population[a1] if fitnesses[a1] < fitnesses[a2] else population[a2]

            # Tournament selection for parent B
            b1, b2 = rng.integers(0, population_size, size=2)
            parent_b = population[b1] if fitnesses[b1] < fitnesses[b2] else population[b2]

            # Single-point crossover
            if rng.random() < crossover_rate:
                point = int(rng.integers(1, dim))  # crossover point in [1, dim-1]
                child = np.concatenate([parent_a[:point], parent_b[point:]])
            else:
                child = parent_a.copy()

            # Per-gene Gaussian mutation
            for gene_idx in range(dim):
                if rng.random() < mutation_rate:
                    if gene_idx < N:
                        # Location score — σ relative to [0,1] range
                        child[gene_idx] += rng.normal(0, 0.1)
                    else:
                        # Fleet size — σ relative to EV range
                        child[gene_idx] += rng.normal(0, 0.1 * (max_evs - min_evs))

            # Clamp to valid bounds after mutation
            child[:N] = np.clip(child[:N], 0.0, 1.0)
            child[N:] = np.clip(child[N:], min_evs, max_evs)

            new_population[child_idx] = child

        population = new_population

    # -----------------------------------------------------------------------
    # Decode and evaluate the best solution found
    # -----------------------------------------------------------------------
    best_allocation = decode_particle(best_chromosome, N, valid_buses, min_evs, max_evs)
    final_result = evaluate_scenario(best_allocation, per_unit_kw_per_ev=per_unit_kw_per_ev)

    return {
        "best_allocation":     best_allocation,
        "best_fitness":        best_fitness,
        "convergence_history": convergence_history,
        "final_voltages":      final_result.get("bus_voltages"),
        "num_violations":      final_result.get("num_violations"),
    }
