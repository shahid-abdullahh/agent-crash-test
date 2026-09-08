from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.schemas.task import Task
from app.agent.tools import ToolDefinition, ToolExecutor
from app.traces.collector import TraceCollector


class BaseAgent(ABC):
    @abstractmethod
    async def run(
        self,
        task: Task,
        tools: List[ToolDefinition],
        tool_executor: ToolExecutor,
        trace_collector: TraceCollector,
    ) -> Dict[str, Any]:
        """Execute the agent loop for the specified task."""
        pass
