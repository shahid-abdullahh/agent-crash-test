from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.agent.tools import ToolDefinition
from app.agent.providers.models import LLMMessage, AgentAction


class LLMProvider(ABC):
    """Abstract interface for language model providers returning structured AgentAction."""

    @abstractmethod
    async def generate_action(
        self,
        messages: List[LLMMessage],
        tools: List[ToolDefinition],
    ) -> AgentAction:
        """
        Evaluate context messages and available tools, returning a structured AgentAction.
        The provider MUST NOT execute tools or directly manipulate environment state.
        """
        pass
