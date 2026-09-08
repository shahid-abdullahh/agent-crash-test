import pytest
import httpx
from app.main import app
from app.services.run_service import run_service
from app.services.comparison_service import comparison_service
from app.schemas.run import RunCreateRequest


@pytest.mark.asyncio
async def test_before_after_remediation_comparison(async_client: httpx.AsyncClient):
    # 1. Run Baseline (Ambiguous Timeout + Unsafe Retry -> FAILED, 2 reservations)
    req_baseline = RunCreateRequest(
        task_id="task-book-cheapest-flight",
        scenario_mode="timeout_after_commit",
        agent_type="deterministic",
        agent_retry_policy="unsafe_retry",
    )
    run_baseline = await run_service.execute_run(req_baseline, custom_client=async_client)
    assert run_baseline.status.value == "failed"

    # 2. Run Remediated (Ambiguous Timeout + Idempotent Key -> COMPLETED, 1 reservation)
    req_remediated = RunCreateRequest(
        task_id="task-book-cheapest-flight",
        scenario_mode="timeout_after_commit",
        agent_type="deterministic",
        agent_retry_policy="idempotent_retry",
    )
    run_remediated = await run_service.execute_run(req_remediated, custom_client=async_client)
    assert run_remediated.status.value == "completed"

    # 3. Perform structured comparison
    comparison = comparison_service.compare_runs(
        baseline_run_id=run_baseline.id,
        remediated_run_id=run_remediated.id,
    )

    assert comparison.status_transition == "FAILED -> COMPLETED"
    assert comparison.remediation_effective is True
    assert comparison.baseline_run.total_reservations == 2
    assert comparison.baseline_run.duplicate_reservations == 1
    assert comparison.remediated_run.total_reservations == 1
    assert comparison.remediated_run.duplicate_reservations == 0
    assert len(comparison.key_findings) > 0

    # 4. Query via HTTP endpoint
    resp = await async_client.get(
        f"/comparison?baseline_run_id={run_baseline.id}&remediated_run_id={run_remediated.id}"
    )
    assert resp.status_code == 200
    comp_json = resp.json()
    assert comp_json["remediation_effective"] is True
    assert comp_json["status_transition"] == "FAILED -> COMPLETED"
