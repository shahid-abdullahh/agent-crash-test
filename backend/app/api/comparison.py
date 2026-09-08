from fastapi import APIRouter, Query
from app.schemas.comparison import RunComparison
from app.services.comparison_service import comparison_service

router = APIRouter(prefix="/comparison", tags=["Run Remediation Comparison"])


@router.get("", response_model=RunComparison)
def compare_runs(
    baseline_run_id: str = Query(..., description="ID of baseline/failed run"),
    remediated_run_id: str = Query(..., description="ID of remediated/successful run"),
):
    """Compare baseline run against remediated run to demonstrate measurable before/after improvement."""
    return comparison_service.compare_runs(baseline_run_id=baseline_run_id, remediated_run_id=remediated_run_id)
