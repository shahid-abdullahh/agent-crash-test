from pydantic import BaseModel
from typing import Dict, Any, List


class TaskReliabilityMetric(BaseModel):
    task_id: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    reliability_percentage: float


class ReliabilityOverview(BaseModel):
    total_runs: int
    successful_runs: int
    failed_runs: int
    overall_reliability_percentage: float
    by_scenario: Dict[str, float]
    by_task: List[TaskReliabilityMetric]
