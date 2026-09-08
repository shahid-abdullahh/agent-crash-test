from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class CriterionResult(BaseModel):
    name: str
    passed: bool
    expected: Any
    actual: Any
    message: str


class SideEffectEvaluation(BaseModel):
    is_safe: bool
    total_reservations_created: int
    expected_reservations: int
    duplicate_reservations_detected: int
    unintended_state_mutations: List[str] = []


class EvaluationResult(BaseModel):
    run_id: str
    task_id: str
    success: bool
    criteria: List[CriterionResult]
    side_effects: SideEffectEvaluation
    reasons: List[str]
    evaluated_at: str
