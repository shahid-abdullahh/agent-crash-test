import json
import uuid
from typing import Dict, Any, List, Optional
from app.agent.base import BaseAgent
from app.agent.tools import ToolDefinition, ToolExecutor
from app.agent.providers.base import LLMProvider
from app.agent.providers.models import LLMMessage, AgentAction, ActionType
from app.schemas.task import Task
from app.schemas.trace import TraceEventType
from app.traces.collector import TraceCollector


SYSTEM_PROMPT = """You are an autonomous API task-solving agent.
Your objective is to accomplish the user-specified task by selecting and calling available API tools.

Rules:
1. You may ONLY call tools that are explicitly provided.
2. Respect all task constraints (budget, origin, destination, names).
3. Inspect tool results carefully to verify operation outcomes before taking subsequent actions.
4. When the task is complete, produce a final response indicating the outcome.
5. Do not guess parameters that are required by the tool schemas.
"""


class LLMAgent(BaseAgent):
    """
    Provider-independent LLM agent that executes a structured decision loop
    over dynamically generated OpenAPI tools.
    """

    def __init__(
        self,
        provider: LLMProvider,
        max_steps: int = 10,
        system_prompt: str = SYSTEM_PROMPT,
    ):
        self.provider = provider
        self.max_steps = max_steps
        self.system_prompt = system_prompt

    async def run(
        self,
        task: Task,
        tools: List[ToolDefinition],
        tool_executor: ToolExecutor,
        trace_collector: TraceCollector,
    ) -> Dict[str, Any]:
        trace_collector.add_event(
            event_type=TraceEventType.AGENT_START,
            metadata={"task_id": task.id, "agent_type": "llm", "max_steps": self.max_steps},
        )

        tools_map = {t.name: t for t in tools}
        messages: List[LLMMessage] = [
            LLMMessage(role="system", content=self.system_prompt),
            LLMMessage(
                role="user",
                content=(
                    f"Task ID: {task.id}\n"
                    f"Task Name: {task.name}\n"
                    f"Description: {task.description}\n"
                    f"Constraints: {task.constraints.model_dump_json()}\n"
                    f"Expected Outcome: {task.expected_outcome_description}"
                ),
            ),
        ]

        step = 0
        while step < self.max_steps:
            step += 1

            # 1. Ask provider for next structured action
            try:
                action = await self.provider.generate_action(messages=messages, tools=tools)
            except Exception as e:
                err_msg = f"LLM Provider invocation failed: {str(e)}"
                trace_collector.add_event(
                    event_type=TraceEventType.ERROR,
                    error_message=err_msg,
                )
                trace_collector.add_event(
                    event_type=TraceEventType.AGENT_OUTPUT,
                    metadata={"final_output": {"success": False, "error": err_msg}},
                )
                return {"success": False, "error": err_msg}

            # 2. Handle FINAL action
            if action.type == ActionType.FINAL:
                if action.thought:
                    trace_collector.add_event(
                        event_type=TraceEventType.AGENT_THINKING,
                        metadata={"thought": action.thought},
                    )

                out = {
                    "success": True,
                    "message": action.message or "Task finished.",
                    "steps_taken": step,
                }
                trace_collector.add_event(
                    event_type=TraceEventType.AGENT_OUTPUT,
                    metadata={"final_output": out},
                )
                return out

            # 3. Handle TOOL_CALL action
            if action.type == ActionType.TOOL_CALL:
                tool_name = action.tool or ""
                arguments = action.arguments or {}
                call_id = f"call_{uuid.uuid4().hex[:8]}"

                if action.thought:
                    trace_collector.add_event(
                        event_type=TraceEventType.AGENT_THINKING,
                        metadata={"thought": action.thought},
                    )

                # Tool Authorization check
                if tool_name not in tools_map:
                    err_text = f"Tool '{tool_name}' is unauthorized or does not exist. Available tools: {list(tools_map.keys())}"
                    trace_collector.add_event(
                        event_type=TraceEventType.ERROR,
                        tool_name=tool_name,
                        error_message=err_text,
                    )
                    messages.append(
                        LLMMessage(
                            role="assistant",
                            action=action,
                            tool_call_id=call_id,
                            content=action.thought,
                        )
                    )
                    messages.append(
                        LLMMessage(
                            role="tool",
                            tool_name=tool_name,
                            tool_call_id=call_id,
                            content=json.dumps({"error": err_text, "is_success": False}),
                        )
                    )
                    continue

                # Argument Validation check against required parameters
                tool_def = tools_map[tool_name]
                required_params = tool_def.parameters.get("required", [])
                missing_params = [p for p in required_params if p not in arguments or arguments[p] is None]

                if missing_params:
                    validation_err = f"Validation Error: Tool '{tool_name}' requires missing parameter(s): {missing_params}"
                    trace_collector.add_event(
                        event_type=TraceEventType.ERROR,
                        tool_name=tool_name,
                        tool_arguments=arguments,
                        error_message=validation_err,
                    )
                    messages.append(
                        LLMMessage(
                            role="assistant",
                            action=action,
                            tool_call_id=call_id,
                            content=action.thought,
                        )
                    )
                    messages.append(
                        LLMMessage(
                            role="tool",
                            tool_name=tool_name,
                            tool_call_id=call_id,
                            content=json.dumps({"error": validation_err, "is_success": False}),
                        )
                    )
                    continue

                # Execute permitted tool via ToolExecutor
                tool_result = await tool_executor.execute(
                    tool_name=tool_name,
                    arguments=arguments,
                    trace_collector=trace_collector,
                )

                # Append result to context messages
                messages.append(
                    LLMMessage(
                        role="assistant",
                        action=action,
                        tool_call_id=call_id,
                        content=action.thought,
                    )
                )
                messages.append(
                    LLMMessage(
                        role="tool",
                        tool_name=tool_name,
                        tool_call_id=call_id,
                        content=json.dumps(tool_result),
                    )
                )

        # Max steps exhausted
        exhausted_msg = f"Agent exceeded maximum allowed step limit ({self.max_steps})."
        trace_collector.add_event(
            event_type=TraceEventType.ERROR,
            error_message=exhausted_msg,
        )
        out = {"success": False, "error": exhausted_msg, "steps_taken": self.max_steps}
        trace_collector.add_event(
            event_type=TraceEventType.AGENT_OUTPUT,
            metadata={"final_output": out},
        )
        return out
