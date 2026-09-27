"""
Particle Swarm Optimization (PSO) module for EV Rental Centre allocation.

Implementation decision:
    PSO is implemented MANUALLY using plain Python + NumPy rather than pyswarms.
    Reason: the problem is mixed-integer (bus selection + integer fleet size), and
    pyswarms assumes purely continuous variables.  The paper's update equations
    (Eqs. 9–15) are simple enough to hand-code cleanly without a library wrapper.

References (base paper):
    - Section 3.2  — fitness function (Eq. 6)
    - Section 3.3  — PSO update rules (Eqs. 9–15)

TUNABLE CONSTANTS (paper does not give exact numeric values; these are our choices):
    C_LOSS = 100   — penalty weight for total active-power loss (MW)
    C_VIOL = 1000  — penalty weight per voltage violation
"""

import numpy as np
from typing import List, Dict, Any, Optional

from app.services.power_flow import evaluate_scenario
from app.services.load_profile import compute_ev_load_profile

# ---------------------------------------------------------------------------
# Tunable penalty constants (Eq. 6)
# ---------------------------------------------------------------------------
C_LOSS: float = 100.0   # Weight for total active-power loss (MW)
C_VIOL: float = 1000.0  # Penalty per voltage-limit violation
# ---------------------------------------------------------------------------


def decode_particle(
    particle: np.ndarray,
    N: int,
    valid_buses: List[int],
    min_evs: int,
    max_evs: int,
) -> Dict[int, int]:
    """Convert a raw continuous particle into a feasible EV-allocation dict.

    The particle vector has length ``2*N``:
        particle[:N]  — location scores (one score per entry in valid_buses,
                        sorted descending to pick the top-N distinct buses)
        particle[N:]  — fleet sizes (continuous, rounded and clipped to bounds)

    Duplicate selection is avoided by picking indices in descending score order
    (argmax loop with score invalidation), so exactly N distinct buses are returned.

    Parameters
    ----------
    particle   : length-2N numpy array
    N          : number of rental centres
    valid_buses: ordered list of candidate bus numbers (e.g. list(range(2,34)))
    min_evs    : minimum EVs per centre
    max_evs    : maximum EVs per centre

    Returns
    -------
    dict {bus_number: num_evs}  with N distinct entries
    """
    loc_scores = particle[:N].copy()   # shape (N,) — indexed into valid_buses
    fleet_raw  = particle[N:]          # shape (N,)

    # Select N distinct buses in descending score order
    scores = loc_scores.tolist()
    selected_buses: List[int] = []
    for _ in range(N):
        idx = int(np.argmax(scores))
        selected_buses.append(valid_buses[idx])
        scores[idx] = -np.inf          # prevent re-selection

    # Round fleet sizes and clip to [min_evs, max_evs]
    fleet_counts = np.clip(np.rint(fleet_raw), min_evs, max_evs).astype(int)

    return {bus: int(cnt) for bus, cnt in zip(selected_buses, fleet_counts)}


def fitness_function(
    allocation: Dict[int, int],
    per_unit_kw_per_ev: Optional[float] = None,
) -> float:
    """Evaluate fitness for a decoded allocation (Eq. 6).

    fitness = (C_LOSS × total_active_loss_mw)
            + (C_VIOL × num_violations)
            - (total EVs placed)

    Lower fitness is better.  Non-convergence returns 1e6.
    """
    result = evaluate_scenario(allocation, per_unit_kw_per_ev=per_unit_kw_per_ev)

    # Non-convergence penalty (power_flow signals this with num_violations = 999)
    if result.get("num_violations", 0) >= 999:
        return 1e6

    total_loss = result.get("total_active_loss_mw") or 0.0
    violations = result.get("num_violations", 0)
    total_evs  = sum(allocation.values())

    return (C_LOSS * total_loss) + (C_VIOL * violations) - total_evs


def run_pso(
    N: int,
    min_evs: int,
    max_evs: int,
    num_particles: int = 20,
    max_iterations: int = 100,
    c1: float = 2.0,
    c2: float = 2.0,
    w_max: float = 0.9,
    w_min: float = 0.4,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Run PSO to optimise EV-rental-centre placement (Eqs. 9–15).

    Particle encoding
    -----------------
    - Dimension  : 2*N
    - particle[:N] — location scores in [0, 1]; mapped to top-N distinct buses
      chosen from valid_buses (buses 2–33, 32 candidates)
    - particle[N:] — fleet sizes in [min_evs, max_evs]; rounded to integers

    Inertia schedule (Eq. 13)
    -------------------------
        w_k = w_max - (w_max - w_min) * (k / k_max)

    Velocity update (Eq. 11)
    ------------------------
        v_{k+1} = w * v_k
                + c1 * r1 * (pbest - x_k)
                + c2 * r2 * (gbest - x_k)

    Position update (Eq. 12)
    ------------------------
        x_{k+1} = x_k + v_{k+1}

    Personal/global best update (Eqs. 14–15)
    -----------------------------------------
        pbest_i updated whenever fitness(x_i) < pbest_fitness_i
        gbest   updated whenever any pbest_i < gbest_fitness

    Parameters
    ----------
    N              : number of rental centre locations
    min_evs        : minimum EVs per centre
    max_evs        : maximum EVs per centre
    num_particles  : swarm size (default 20 — paper value)
    max_iterations : maximum iterations (default 100 — paper value)
    c1, c2         : acceleration coefficients (default 2 — paper value)
    w_max, w_min   : inertia bounds (default 0.9 / 0.4 — paper values)
    verbose        : if True, print best fitness after every iteration

    Returns
    -------
    dict with keys:
        best_allocation   : {bus: num_evs}
        best_fitness      : float
        convergence_history : [float] — gbest fitness at each iteration
        final_voltages    : {bus: voltage_pu} or None
        num_violations    : int
    """
    valid_buses: List[int] = list(range(2, 34))  # buses 2–33 (32 candidates)
    dim = 2 * N

    # Pre-compute EV load profile once (avoid redundant CSV reads each evaluation)
    _, per_unit_kw_per_ev = compute_ev_load_profile()

    rng = np.random.default_rng()

    # -----------------------------------------------------------------------
    # Initialise positions and velocities
    # -----------------------------------------------------------------------
    # Location-score portion: uniform in [0, 1]
    # Fleet-size portion    : uniform in [min_evs, max_evs]
    positions = np.empty((num_particles, dim))
    positions[:, :N] = rng.random((num_particles, N))
    positions[:, N:] = min_evs + rng.random((num_particles, N)) * (max_evs - min_evs)

    velocities = np.zeros((num_particles, dim))

    # -----------------------------------------------------------------------
    # Personal bests (Eq. 14)
    # -----------------------------------------------------------------------
    pbest_pos = positions.copy()
    pbest_fit = np.full(num_particles, np.inf)

    # -----------------------------------------------------------------------
    # Global best (Eq. 15)
    # -----------------------------------------------------------------------
    gbest_pos: Optional[np.ndarray] = None
    gbest_fit: float = np.inf
    convergence_history: List[float] = []

    # -----------------------------------------------------------------------
    # Main PSO loop
    # -----------------------------------------------------------------------
    for k in range(max_iterations):
        # Inertia weight (Eq. 13)
        w = w_max - (w_max - w_min) * (k / max_iterations)

        # Evaluate all particles
        for i in range(num_particles):
            alloc = decode_particle(positions[i], N, valid_buses, min_evs, max_evs)
            fit   = fitness_function(alloc, per_unit_kw_per_ev=per_unit_kw_per_ev)

            # Update personal best (Eq. 14)
            if fit < pbest_fit[i]:
                pbest_fit[i] = fit
                pbest_pos[i] = positions[i].copy()

            # Update global best (Eq. 15)
            if fit < gbest_fit:
                gbest_fit = fit
                gbest_pos = positions[i].copy()

        convergence_history.append(float(gbest_fit))

        if verbose:
            print(f"  Iter {k+1:4d}/{max_iterations}  gbest_fitness={gbest_fit:.4f}")

        # Velocity update (Eq. 11)
        r1 = rng.random((num_particles, dim))
        r2 = rng.random((num_particles, dim))
        velocities = (
            w * velocities
            + c1 * r1 * (pbest_pos - positions)
            + c2 * r2 * (gbest_pos - positions)
        )

        # Position update (Eq. 12)
        positions = positions + velocities

        # Clamp to valid bounds
        positions[:, :N] = np.clip(positions[:, :N], 0.0, 1.0)
        positions[:, N:] = np.clip(positions[:, N:], min_evs, max_evs)

    # -----------------------------------------------------------------------
    # Decode and evaluate the final global best
    # -----------------------------------------------------------------------
    best_allocation = decode_particle(gbest_pos, N, valid_buses, min_evs, max_evs)
    final_result    = evaluate_scenario(best_allocation, per_unit_kw_per_ev=per_unit_kw_per_ev)

    return {
        "best_allocation":    best_allocation,
        "best_fitness":       float(gbest_fit),
        "convergence_history": convergence_history,
        "final_voltages":     final_result.get("bus_voltages"),
        "num_violations":     final_result.get("num_violations"),
    }
