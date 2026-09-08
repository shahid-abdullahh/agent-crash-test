import pytest
import httpx
from app.main import app
from app.services.run_service import RunService
from app.schemas.run import RunCreateRequest, RunStatus


@pytest.mark.asyncio
async def test_failure_injection_timeout_after_commit_with_unsafe_retry():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        service = RunService(base_url="http://testserver")
        req = RunCreateRequest(
            task_id="task-book-cheapest-flight",
            scenario_mode="timeout_after_commit",
            agent_type="deterministic",
            agent_retry_policy="unsafe_retry",
        )
        run = await service.execute_run(req, custom_client=client)

        # Run must fail because duplicate reservations were created
        assert run.status == RunStatus.FAILED
        assert run.evaluation is not None
        assert run.evaluation.success is False
        assert run.evaluation.side_effects.is_safe is False
        assert run.evaluation.side_effects.total_reservations_created == 2
        assert run.evaluation.side_effects.duplicate_reservations_detected == 1

        # Check diagnosis is attached
        assert run.diagnosis is not None
        assert "Ambiguous Operation Outcome" in run.diagnosis.failure_category
        assert "Idempotency-Key" in run.diagnosis.recommended_remediation


@pytest.mark.asyncio
async def test_remediation_with_idempotent_retry_avoids_duplicate():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        service = RunService(base_url="http://testserver")
        req = RunCreateRequest(
            task_id="task-book-cheapest-flight",
            scenario_mode="timeout_after_commit",
            agent_type="deterministic",
            agent_retry_policy="idempotent_retry",
        )
        run = await service.execute_run(req, custom_client=client)

        # When agent retries with the same Idempotency-Key, sandbox returns existing reservation
        assert run.status == RunStatus.COMPLETED
        assert run.evaluation is not None
        assert run.evaluation.success is True
        assert run.evaluation.side_effects.is_safe is True
        assert run.evaluation.side_effects.total_reservations_created == 1
        assert run.evaluation.side_effects.duplicate_reservations_detected == 0
