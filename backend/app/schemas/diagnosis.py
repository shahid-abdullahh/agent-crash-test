from pydantic import BaseModel
from typing import List, Optional


class DiagnosisResult(BaseModel):
    failure_category: str
    observed_behavior: str
    agent_behavior: str
    impact: str
    likely_responsibility: str  # e.g. "Agent / API Integration Pattern"
    recommended_remediation: str
    evidence_events: List[str] = []
