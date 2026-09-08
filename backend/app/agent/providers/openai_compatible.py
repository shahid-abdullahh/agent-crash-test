import os
import json
import httpx
from typing import List, Dict, Any, Optional
from app.agent.providers.base import LLMProvider
from app.agent.providers.models import LLMMessage, AgentAction, ActionType
from app.agent.tools import ToolDefinition


class OpenAICompatibleProvider(LLMProvider):
    """
    Real LLM provider communicating over the standard OpenAI-compatible Chat Completions HTTP protocol
    with structured tool calling support. Supports OpenAI, vLLM, Ollama, LocalAI, and compatible gateways.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate_action(
        self,
        messages: List[LLMMessage],
        tools: List[ToolDefinition],
    ) -> AgentAction:
        if not self.is_configured():
            raise RuntimeError(
                "OpenAICompatibleProvider is not configured with an API key. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        # 1. Format tools for OpenAI Chat Completions API
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in tools
        ]

        # 2. Format messages
        openai_messages = []
        for msg in messages:
            if msg.role == "tool":
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id or "call_default",
                    "content": msg.content or "",
                })
            elif msg.role == "assistant" and msg.action and msg.action.type == ActionType.TOOL_CALL:
                openai_messages.append({
                    "role": "assistant",
                    "content": msg.content or None,
                    "tool_calls": [
                        {
                            "id": msg.tool_call_id or "call_default",
                            "type": "function",
                            "function": {
                                "name": msg.action.tool,
                                "arguments": json.dumps(msg.action.arguments),
                            },
                        }
                    ],
                })
            else:
                openai_messages.append({
                    "role": msg.role,
                    "content": msg.content or "",
                })

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": openai_messages,
        }
        if openai_tools:
            payload["tools"] = openai_tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if not response.is_success:
                raise RuntimeError(
                    f"LLM Provider API error ({response.status_code}): {response.text}"
                )

            data = response.json()
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})

            # Check if model invoked a tool call
            tool_calls = message.get("tool_calls")
            if tool_calls and len(tool_calls) > 0:
                first_call = tool_calls[0]
                func = first_call.get("function", {})
                tool_name = func.get("name", "")
                raw_args = func.get("arguments", "{}")
                try:
                    parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception:
                    parsed_args = {}

                return AgentAction(
                    type=ActionType.TOOL_CALL,
                    tool=tool_name,
                    arguments=parsed_args if isinstance(parsed_args, dict) else {},
                    thought=message.get("content"),
                )

            # Otherwise, model produced final response text
            content_text = message.get("content", "Task completed.")
            return AgentAction(
                type=ActionType.FINAL,
                message=content_text,
                thought=content_text,
            )
