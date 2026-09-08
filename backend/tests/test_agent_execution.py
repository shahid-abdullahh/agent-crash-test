import pytest
import httpx
from app.main import app
from app.services.run_service import RunService
from app.schemas.run import RunCreateRequest, RunStatus


@pytest.mark.asyncio
async def test_agent_execution_happy_path():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        service = RunService(base_url="http://testserver")
        req = RunCreateRequest(
            task_id="task-book-cheapest-flight",
            scenario_mode="normal",
            agent_type="deterministic",
            agent_retry_policy="unsafe_retry",
        )
        run = await service.execute_run(req, custom_client=client)

        assert run.status == RunStatus.COMPLETED
        assert run.evaluation is not None
        assert run.evaluation.success is True
        assert run.evaluation.side_effects.is_safe is True
        assert run.evaluation.side_effects.total_reservations_created == 1
        assert run.final_output is not None
        assert run.final_output["success"] is True
        assert run.final_output["flight_id"] == "FL-101"
        assert run.final_output["price_paid"] == 6500.0

        # Verify trace has complete execution loop
        event_types = [e.event_type.value for e in run.trace]
        assert "agent_start" in event_types
        assert "agent_thinking" in event_types
        assert "tool_call" in event_types
        assert "http_request" in event_types
        assert "http_response" in event_types
        assert "agent_output" in event_types
