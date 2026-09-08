from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, Optional, List, Literal
from enum import Enum


class ActionType(str, Enum):
    TOOL_CALL = "tool_call"
    FINAL = "final"


class AgentAction(BaseModel):
    type: ActionType
    tool: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    thought: Optional[str] = None

    @model_validator(mode="after")
    def validate_action_fields(self) -> "AgentAction":
        if self.type == ActionType.TOOL_CALL:
            if not self.tool:
                raise ValueError("Tool name is required when action type is 'tool_call'")
        elif self.type == ActionType.FINAL:
            if not self.message:
                self.message = "Task completed."
        return self


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None
    action: Optional[AgentAction] = None
