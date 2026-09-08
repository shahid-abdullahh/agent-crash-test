from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class EndpointDoc(BaseModel):
    operation_id: str
    method: str
    path: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    request_example: Optional[Dict[str, Any]] = None
    response_examples: Dict[str, Any] = Field(default_factory=dict)
    state_changing: bool = False
    agent_guidance: str
    recovery_considerations: str


class APIDocumentation(BaseModel):
    integration_id: str
    title: str
    version: str
    base_url: str
    overview: str
    auth_summary: str
    endpoints: List[EndpointDoc] = Field(default_factory=list)
    agent_usage_rules: List[str] = Field(default_factory=list)
    failure_and_recovery_guide: List[str] = Field(default_factory=list)
    markdown_content: str
    generated_at: str
