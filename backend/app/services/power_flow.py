"""
Power Flow Evaluation Engine for Modified IEEE 33-Bus Radial Distribution Network.

This module builds a pandapower network model representing the 33-bus system with a
3.6 MW DG unit at Bus 6, and provides scenario evaluation for EV fleet allocations.

Performance note (Task 6 Part A):
    The base network is built ONCE at first use and stored in a module-level singleton
    (_BASE_NET_CACHE).  Every call to evaluate_scenario() deep-copies this cached
    network instead of re-parsing both CSVs and reconstructing all 33 buses / 32 lines
    from scratch.  pandapower's copy.deepcopy() is used as recommended by the library.
    This removes CSV I/O and object-construction overhead from the hot path, giving a
    significant speed-up when PSO/GA call evaluate_scenario() hundreds of times.
"""

import copy
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import pandapower as pp

from app.services.load_profile import compute_ev_load_profile

# ---------------------------------------------------------------------------
# Module-level base-network singleton (built once, deep-copied per scenario)
# ---------------------------------------------------------------------------
_BASE_NET_CACHE: Optional[pp.pandapowerNet] = None


def get_base_network(
    bus_loads_path: Optional[str] = None,
    line_params_path: Optional[str] = None,
) -> pp.pandapowerNet:
    """Return the cached base network, building it on first call.

    Subsequent calls with the same (default) paths return the already-built
    network instantly without any CSV or pandapower construction overhead.
    """
    global _BASE_NET_CACHE
    if _BASE_NET_CACHE is None:
        _BASE_NET_CACHE = build_network(
            bus_loads_path=bus_loads_path,
            line_params_path=line_params_path,
        )
    return _BASE_NET_CACHE


def get_data_dir() -> Path:
    """Resolve the directory containing network dataset CSV files."""
    return Path(__file__).resolve().parent.parent.parent / "data"


def build_network(
    bus_loads_path: Optional[str] = None,
    line_params_path: Optional[str] = None,
) -> pp.pandapowerNet:
    """
    Constructs a fresh pandapower network instance representing the modified
    IEEE 33-bus radial distribution network.

    Parameters
    ----------
    bus_loads_path : str, optional
        Path to bus_loads.csv.
    line_params_path : str, optional
        Path to line_params.csv.

    Returns
    -------
    net : pp.pandapowerNet
        Freshly built pandapower network.
    """
    data_dir = get_data_dir()
    if bus_loads_path is None:
        bus_loads_path = str(data_dir / "bus_loads.csv")
    if line_params_path is None:
        line_params_path = str(data_dir / "line_params.csv")

    # Base parameters for standard 33-bus radial distribution system
    vn_kv = 12.66  # Base voltage (kV)
    sn_mva = 10.0  # Base apparent power (MVA)
    zb_ohm = (vn_kv**2) / sn_mva  # Base impedance (Ohm) = 16.027556 Ohm

    net = pp.create_empty_network(sn_mva=sn_mva)

    bus_loads_df = pd.read_csv(bus_loads_path)
    line_params_df = pd.read_csv(line_params_path)

    # 1. Create buses (1..33)
    bus_map = {}
    for _, row in bus_loads_df.iterrows():
        node = int(row["node"])
        b_idx = pp.create_bus(net, vn_kv=vn_kv, name=f"Bus {node}", index=node)
        bus_map[node] = b_idx

        # Static active & reactive loads
        p_mw = float(row["active_mw"])
        q_mvar = float(row["reactive_mvar"])
        if p_mw > 0.0 or q_mvar > 0.0:
            pp.create_load(
                net,
                bus=b_idx,
                p_mw=p_mw,
                q_mvar=q_mvar,
                name=f"Load_Bus_{node}",
            )

    # 2. Slack bus (Grid connection at Bus 1)
    pp.create_ext_grid(net, bus=bus_map[1], vm_pu=1.0, va_degree=0.0, name="Grid_Slack_Bus_1")

    # 3. Distributed Generation (3.6 MW DG at Bus 6 per base paper)
    pp.create_sgen(net, bus=bus_map[6], p_mw=3.6, q_mvar=0.0, name="DG_Bus_6")

    # 4. Branch lines (32 lines)
    for _, row in line_params_df.iterrows():
        fn = int(row["from_node"])
        tn = int(row["to_node"])
        r_pu = float(row["resistance_pu"])
        x_pu = float(row["reactance_pu"])

        r_ohm = r_pu * zb_ohm
        x_ohm = x_pu * zb_ohm

        pp.create_line_from_parameters(
            net,
            from_bus=bus_map[fn],
            to_bus=bus_map[tn],
            length_km=1.0,
            r_ohm_per_km=r_ohm,
            x_ohm_per_km=x_ohm,
            c_nf_per_km=0.0,
            max_i_ka=1.0,
            name=f"Line_{fn}_{tn}",
        )

    # Store bus_map in network for easy lookup
    net._bus_map = bus_map

    return net


def evaluate_scenario(
    ev_allocation: Dict[int, int],
    per_unit_kw_per_ev: Optional[float] = None,
    bus_loads_path: Optional[str] = None,
    line_params_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluates AC power flow for a given EV allocation across network buses.

    Parameters
    ----------
    ev_allocation : dict[int, int]
        Mapping of bus number (1..33) to number of allocated EVs, e.g. {2: 100, 4: 100}.
    per_unit_kw_per_ev : float, optional
        Peak per-unit EV charging demand (kW/EV). If None, calculated from behavior dataset.
    bus_loads_path : str, optional
        Path to bus_loads.csv.
    line_params_path : str, optional
        Path to line_params.csv.

    Returns
    -------
    dict
        {
            "bus_voltages": {1: 1.0, 2: 0.998, ... 33: 0.965},  # None if non-converged
            "total_active_loss_mw": float,                     # None if non-converged
            "voltage_violations": [list of violating bus IDs],
            "num_violations": int                              # 999 penalty if non-converged
        }
    """
    if per_unit_kw_per_ev is None:
        _, per_unit_kw_per_ev = compute_ev_load_profile()

    # Deep-copy the cached base network (avoids re-parsing CSVs on every call).
    # Each copy is fully isolated — EV load additions do not leak between scenarios.
    net = copy.deepcopy(get_base_network(
        bus_loads_path=bus_loads_path,
        line_params_path=line_params_path,
    ))
    bus_map = getattr(net, "_bus_map", {i: i for i in range(1, 34)})

    # Add extra EV loads at specified buses
    for bus_num, num_evs in ev_allocation.items():
        if num_evs > 0 and bus_num in bus_map:
            extra_p_mw = (num_evs * per_unit_kw_per_ev) / 1000.0  # Convert kW to MW
            pp.create_load(
                net,
                bus=bus_map[bus_num],
                p_mw=extra_p_mw,
                q_mvar=0.0,
                name=f"EV_Load_Bus_{bus_num}",
            )

    try:
        # Run AC power flow
        pp.runpp(net, numba=False, max_iteration=50)

        # Extract bus voltages
        bus_voltages: Dict[int, float] = {}
        voltage_violations: List[int] = []

        for node, b_idx in bus_map.items():
            vm = float(net.res_bus.loc[b_idx, "vm_pu"])
            bus_voltages[node] = round(vm, 6)
            if vm < 0.95 or vm > 1.05:
                voltage_violations.append(node)

        total_loss_mw = float(net.res_line.pl_mw.sum())

        return {
            "bus_voltages": bus_voltages,
            "total_active_loss_mw": round(total_loss_mw, 6),
            "voltage_violations": voltage_violations,
            "num_violations": len(voltage_violations),
        }

    except Exception as e:
        # Non-convergence or numerical error penalty
        return {
            "bus_voltages": None,
            "total_active_loss_mw": None,
            "voltage_violations": [],
            "num_violations": 999,
        }
