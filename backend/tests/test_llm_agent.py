import os
import pytest
import httpx
from app.main import app
from app.agent.llm_agent import LLMAgent
from app.agent.tools import get_travel_tools, ToolExecutor
from app.agent.providers.models import AgentAction, ActionType, LLMMessage
from app.agent.providers.mock import MockLLMProvider
from app.agent.providers.openai_compatible import OpenAICompatibleProvider
from app.traces.collector import TraceCollector
from app.services.task_service import task_service
from app.services.run_service import RunService
from app.schemas.run import RunCreateRequest, RunStatus


def test_agent_action_validation():
    # Valid tool call
    action = AgentAction(type=ActionType.TOOL_CALL, tool="search_flights", arguments={"origin": "DEL"})
    assert action.type == ActionType.TOOL_CALL
    assert action.tool == "search_flights"

    # Valid final action
    final_action = AgentAction(type=ActionType.FINAL, message="Finished booking.")
    assert final_action.type == ActionType.FINAL
    assert final_action.message == "Finished booking."

    # Invalid tool call without tool name
    with pytest.raises(ValueError):
        AgentAction(type=ActionType.TOOL_CALL, tool=None)


@pytest.mark.asyncio
async def test_llm_agent_multi_step_loop(async_client: httpx.AsyncClient):
    # Setup planned sequence of actions in mock provider
    planned_actions = [
        AgentAction(
            type=ActionType.TOOL_CALL,
            tool="search_flights",
            arguments={"origin": "DEL", "destination": "BOM", "max_price": 8000},
            thought="Step 1: Searching for flights within budget.",
        ),
        AgentAction(
            type=ActionType.TOOL_CALL,
            tool="get_flight",
            arguments={"flight_id": "FL-101"},
            thought="Step 2: Checking seat availability for FL-101.",
        ),
        AgentAction(
            type=ActionType.TOOL_CALL,
            tool="create_reservation",
            arguments={"flight_id": "FL-101", "passenger_name": "Deepa Nair"},
            thought="Step 3: Booking flight FL-101.",
        ),
        AgentAction(
            type=ActionType.FINAL,
            message="Flight FL-101 booked successfully for Deepa Nair.",
            thought="Completed task.",
        ),
    ]

    mock_provider = MockLLMProvider(planned_actions=planned_actions)
    agent = LLMAgent(provider=mock_provider, max_steps=10)

    tools = get_travel_tools()
    executor = ToolExecutor(base_url="http://testserver", client=async_client, tools=tools)
    collector = TraceCollector(run_id="run-llm-loop-test")

    task = task_service.get_task("task-book-cheapest-flight")
    assert task is not None

    result = await agent.run(task, tools, executor, collector)
    assert result["success"] is True
    assert "Deepa Nair" in result["message"]

    # Verify Trace recorded observable actions
    events = collector.get_events()
    event_types = [e.event_type.value for e in events]
    assert "agent_start" in event_types
    assert "agent_thinking" in event_types
    assert "tool_call" in event_types
    assert "http_request" in event_types
    assert "http_response" in event_types
    assert "tool_result" in event_types
    assert "agent_output" in event_types

    # Verify conversation context grew properly across tool calls
    assert mock_provider.invocations_count == 4


@pytest.mark.asyncio
async def test_llm_agent_unauthorized_tool_safety(async_client: httpx.AsyncClient):
    planned_actions = [
        AgentAction(
            type=ActionType.TOOL_CALL,
            tool="unauthorized_exec_shell",
            arguments={"cmd": "rm -rf /"},
            thought="Trying unauthorized tool",
        ),
        AgentAction(
            type=ActionType.FINAL,
            message="Safely finished after error.",
        ),
    ]
    mock_provider = MockLLMProvider(planned_actions=planned_actions)
    agent = LLMAgent(provider=mock_provider, max_steps=5)

    tools = get_travel_tools()
    executor = ToolExecutor(base_url="http://testserver", client=async_client, tools=tools)
    collector = TraceCollector(run_id="run-llm-security-test")
    task = task_service.get_task("task-book-cheapest-flight")

    result = await agent.run(task, tools, executor, collector)
    assert result["success"] is True

    # Verify unauthorized tool never executed via HTTP
    events = collector.get_events()
    http_events = [e for e in events if e.http_payload]
    assert not any("/unauthorized" in (e.http_payload.url or "") for e in http_events)
    # Verify error was logged in trace
    error_events = [e for e in events if e.error_message]
    assert any("unauthorized" in e.error_message for e in error_events)


@pytest.mark.asyncio
async def test_llm_agent_invalid_arguments_validation(async_client: httpx.AsyncClient):
    planned_actions = [
        # Missing required parameter passenger_name
        AgentAction(
            type=ActionType.TOOL_CALL,
            tool="create_reservation",
            arguments={"flight_id": "FL-101"},
        ),
        AgentAction(
            type=ActionType.FINAL,
            message="Stopped due to validation error.",
        ),
    ]
    mock_provider = MockLLMProvider(planned_actions=planned_actions)
    agent = LLMAgent(provider=mock_provider, max_steps=5)

    tools = get_travel_tools()
    executor = ToolExecutor(base_url="http://testserver", client=async_client, tools=tools)
    collector = TraceCollector(run_id="run-llm-validation-test")
    task = task_service.get_task("task-book-cheapest-flight")

    await agent.run(task, tools, executor, collector)

    # Verify validation error was emitted without crashing
    events = collector.get_events()
    error_events = [e for e in events if e.error_message]
    assert any("missing parameter" in e.error_message.lower() for e in error_events)


@pytest.mark.asyncio
async def test_llm_agent_max_steps_exhaustion(async_client: httpx.AsyncClient):
    # An infinite loop of search_flights
    planned_actions = [
        AgentAction(
            type=ActionType.TOOL_CALL,
            tool="search_flights",
            arguments={"origin": "DEL"},
        )
        for _ in range(10)
    ]
    mock_provider = MockLLMProvider(planned_actions=planned_actions)
    agent = LLMAgent(provider=mock_provider, max_steps=3)

    tools = get_travel_tools()
    executor = ToolExecutor(base_url="http://testserver", client=async_client, tools=tools)
    collector = TraceCollector(run_id="run-llm-max-steps-test")
    task = task_service.get_task("task-book-cheapest-flight")

    result = await agent.run(task, tools, executor, collector)
    assert result["success"] is False
    assert "exceeded maximum allowed step limit" in result["error"]


@pytest.mark.asyncio
async def test_llm_agent_integration_with_evaluation(async_client: httpx.AsyncClient):
    planned_actions = [
        AgentAction(
            type=ActionType.TOOL_CALL,
            tool="search_flights",
            arguments={"origin": "DEL", "destination": "BOM"},
        ),
        AgentAction(
            type=ActionType.TOOL_CALL,
            tool="create_reservation",
            arguments={"flight_id": "FL-101", "passenger_name": "Rahul Sharma"},
        ),
        AgentAction(
            type=ActionType.FINAL,
            message="Reservation confirmed.",
        ),
    ]
    mock_provider = MockLLMProvider(planned_actions=planned_actions)
    mock_agent = LLMAgent(provider=mock_provider, max_steps=10)

    service = RunService(base_url="http://testserver")
    req = RunCreateRequest(
        task_id="task-book-cheapest-flight",
        scenario_mode="normal",
        agent_type="llm",
        agent_retry_policy="unsafe_retry",
    )
    run = await service.execute_run(req, custom_client=async_client, custom_agent=mock_agent)

    # Evaluator must independently inspect state and pass
    assert run.status == RunStatus.COMPLETED
    assert run.evaluation is not None
    assert run.evaluation.success is True
    assert run.evaluation.side_effects.is_safe is True
    assert run.evaluation.side_effects.total_reservations_created == 1


@pytest.mark.asyncio
async def test_real_openai_compatible_provider_optional():
    """Real provider integration test: runs only when OPENAI_API_KEY is configured in the environment."""
    provider = OpenAICompatibleProvider()
    if not provider.is_configured():
        pytest.skip("OPENAI_API_KEY is not configured; skipping real provider live network test.")

    tools = get_travel_tools()
    messages = [
        LLMMessage(role="system", content="You are a travel helper."),
        LLMMessage(role="user", content="What flights are available from DEL to BOM under 8000 INR?"),
    ]
    action = await provider.generate_action(messages, tools)
    assert action.type in (ActionType.TOOL_CALL, ActionType.FINAL)
