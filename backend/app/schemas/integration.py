from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class IntegrationStatus(str, Enum):
    PARSED = "PARSED"
    TOOLS_GENERATED = "TOOLS_GENERATED"
    SCHEMAS_VALID = "SCHEMAS_VALID"
    READY_FOR_TESTING = "READY_FOR_TESTING"


class FindingStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    INFO = "INFO"


class ReadinessFinding(BaseModel):
    category: str
    status: FindingStatus
    title: str
    detail: str


class OperationDefinition(BaseModel):
    operation_id: str
    method: str
    path: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schemas: Dict[str, Any] = Field(default_factory=dict)
    state_changing: bool = False
    idempotency_supported: bool = False
    generated_tool_name: str


class Integration(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    base_url: str
    spec_type: str = "openapi_3.x"
    raw_spec: Dict[str, Any] = Field(default_factory=dict)
    operations: List[OperationDefinition] = Field(default_factory=list)
    schemas: Dict[str, Any] = Field(default_factory=dict)
    generated_tools_count: int = 0
    readiness_findings: List[ReadinessFinding] = Field(default_factory=list)
    status: IntegrationStatus = IntegrationStatus.READY_FOR_TESTING
    created_at: str


class IntegrationCreateRequest(BaseModel):
    name: str
    spec_url: Optional[str] = None
    spec_content: Optional[str] = None  # JSON or YAML string
    base_url_override: Optional[str] = None
