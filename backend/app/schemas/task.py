from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class TaskConstraints(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    max_price: Optional[float] = None
    passenger_name: Optional[str] = None
    criteria_type: str = "cheapest_under_budget"  # e.g. "cheapest_under_budget", "exact_flight"


class Task(BaseModel):
    id: str
    name: str
    description: str
    constraints: TaskConstraints
    expected_outcome_description: str
