from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.schemas.run import Run


class RunComparisonSummary(BaseModel):
    run_id: str
    scenario_mode: str
    agent_type: str
    agent_retry_policy: str
    status: str
    total_reservations: int
    duplicate_reservations: int
    is_safe: bool
    trace_events_count: int
    duration_ms: Optional[float] = None
    failure_category: Optional[str] = None


class RunComparison(BaseModel):
    baseline_run: RunComparisonSummary
    remediated_run: RunComparisonSummary
    status_transition: str  # e.g. "FAILED -> COMPLETED"
    side_effect_delta: str  # e.g. "2 reservations (1 duplicate) -> 1 clean reservation (0 duplicates)"
    trace_event_delta: int  # difference in trace events
    remediation_strategy: str  # e.g. "Idempotent Key Strategy"
    remediation_effective: bool
    key_findings: List[str]
