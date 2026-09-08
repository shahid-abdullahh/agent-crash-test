from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from app.schemas.trace import TraceEvent
from app.schemas.evaluation import EvaluationResult
from app.schemas.diagnosis import DiagnosisResult


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RunCreateRequest(BaseModel):
    task_id: str
    scenario_mode: str = "normal"  # "normal" or "timeout_after_commit"
    agent_type: str = "deterministic"  # "deterministic" or "llm" (when configured)
    agent_retry_policy: str = "unsafe_retry"  # "unsafe_retry" or "idempotent_retry"


class Run(BaseModel):
    id: str
    task_id: str
    scenario_mode: str
    agent_type: str
    agent_retry_policy: str
    status: RunStatus
    trace: List[TraceEvent] = []
    evaluation: Optional[EvaluationResult] = None
    diagnosis: Optional[DiagnosisResult] = None
    created_at: str
    completed_at: Optional[str] = None
    final_output: Optional[Dict[str, Any]] = None
