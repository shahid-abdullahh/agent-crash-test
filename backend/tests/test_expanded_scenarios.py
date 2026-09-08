import pytest
import httpx
from app.main import app
from app.services.run_service import run_service
from app.schemas.run import RunCreateRequest, RunStatus


@pytest.mark.asyncio
async def test_scenario_constraint_violation_api_success_vs_task_failure(async_client: httpx.AsyncClient):
    """Proves that an agent booking an over-budget flight (₹9,200 > ₹8,000) causes task evaluation failure even though the API returns HTTP 200 OK."""
    req = RunCreateRequest(
        task_id="task-book-cheapest-flight",
        scenario_mode="normal",
        agent_type="deterministic",
        agent_retry_policy="violating_agent",
    )
    run = await run_service.execute_run(req, custom_client=async_client)

    # Task evaluation must fail because budget constraint was violated
    assert run.status == RunStatus.FAILED
    assert run.evaluation is not None
    assert run.evaluation.success is False
    budget_criterion = next(c for c in run.evaluation.criteria if c.name == "budget_constraint")
    assert budget_criterion.passed is False
    assert budget_criterion.actual == 9200.0


@pytest.mark.asyncio
async def test_scenario_invalid_parameter_recovery(async_client: httpx.AsyncClient):
    """Proves agent parameter error handling and recovery when API returns HTTP 422 validation error."""
    req = RunCreateRequest(
        task_id="task-book-cheapest-flight",
        scenario_mode="invalid_parameter",
        agent_type="deterministic",
        agent_retry_policy="unsafe_retry",
    )
    run = await run_service.execute_run(req, custom_client=async_client)

    # After recovering from 422 on first attempt, second attempt succeeds
    assert run.status == RunStatus.COMPLETED
    assert run.evaluation is not None
    assert run.evaluation.success is True
    # Verify 422 was captured in trace
    http_responses = [e for e in run.trace if e.http_payload and e.http_payload.status_code]
    status_codes = [e.http_payload.status_code for e in http_responses]
    assert 422 in status_codes
    assert 200 in status_codes
