from typing import List, Optional, Callable, Dict, Any
from app.agent.providers.base import LLMProvider
from app.agent.providers.models import LLMMessage, AgentAction, ActionType
from app.agent.tools import ToolDefinition


class MockLLMProvider(LLMProvider):
    """
    Deterministic mock provider for automated testing of the LLMAgent loop,
    tool authorization, argument validation, and trace recording.
    """

    def __init__(
        self,
        planned_actions: Optional[List[AgentAction]] = None,
        action_generator: Optional[Callable[[List[LLMMessage], List[ToolDefinition]], AgentAction]] = None,
    ):
        self.planned_actions: List[AgentAction] = list(planned_actions) if planned_actions else []
        self.action_generator = action_generator
        self.invocations_count = 0
        self.recorded_history: List[List[LLMMessage]] = []

    async def generate_action(
        self,
        messages: List[LLMMessage],
        tools: List[ToolDefinition],
    ) -> AgentAction:
        self.invocations_count += 1
        self.recorded_history.append(list(messages))

        if self.action_generator:
            return self.action_generator(messages, tools)

        if self.planned_actions:
            return self.planned_actions.pop(0)

        # Default fallback when planned actions are exhausted
        return AgentAction(
            type=ActionType.FINAL,
            message="Mock provider finished all planned actions.",
        )
