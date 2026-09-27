"""
Optimizer Benchmark Results API route — Task 9.

Serves precomputed PSO & GA benchmark results from Task 6 for the dashboard.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/optimizer", tags=["Optimizer"])

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_BENCHMARK_PATH = _DATA_DIR / "benchmark_results.json"


@router.get(
    "/results",
    summary="Get precomputed PSO vs GA benchmark comparison results",
)
def get_optimizer_results():
    if not _BENCHMARK_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benchmark results not found. Run Task 6 benchmark first.",
        )
    try:
        with open(_BENCHMARK_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read benchmark results: {str(e)}",
        )
