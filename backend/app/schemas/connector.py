from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class ConnectorStatus(str, Enum):
    CONNECTED = "CONNECTED"
    READY_FOR_TESTING = "READY_FOR_TESTING"
    TESTED = "TESTED"


class ConnectorDefinition(BaseModel):
    id: str
    name: str
    integration_id: str
    auth_type: str = "none"
    base_url: str
    operations_count: int = 0
    operations: List[str] = Field(default_factory=list)
    status: ConnectorStatus = ConnectorStatus.CONNECTED
    metadata: Dict[str, Any] = Field(default_factory=dict)
