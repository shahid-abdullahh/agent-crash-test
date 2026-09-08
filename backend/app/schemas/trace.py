from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime


class TraceEventType(str, Enum):
    AGENT_START = "agent_start"
    AGENT_THINKING = "agent_thinking"
    TOOL_CALL = "tool_call"
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
    TOOL_RESULT = "tool_result"
    AGENT_OUTPUT = "agent_output"
    ERROR = "error"


class HTTPPayload(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None
    status_code: Optional[int] = None
    response_body: Optional[Any] = None
    duration_ms: Optional[float] = None


class TraceEvent(BaseModel):
    event_id: str
    run_id: str
    sequence_number: int
    timestamp: str
    event_type: TraceEventType
    tool_name: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    http_payload: Optional[HTTPPayload] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
