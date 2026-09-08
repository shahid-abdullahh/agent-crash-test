import pytest
import httpx
from app.services.run_service import run_service


@pytest.mark.asyncio
async def test_complete_vertical_product_slice(async_client: httpx.AsyncClient):
    # Ensure run_service uses the test async_client
    # 1. Fetch available tasks
    tasks_resp = await async_client.get("/tasks")
    assert tasks_resp.status_code == 200
    tasks = tasks_resp.json()
    assert len(tasks) >= 1
    task_id = tasks[0]["id"]

    # 2. Execute Happy Path Run
    # In ASGI test client environment, pass async_client directly to run_service
    happy_req = {
        "task_id": task_id,
        "scenario_mode": "normal",
        "agent_type": "deterministic",
        "agent_retry_policy": "unsafe_retry",
    }
    # Execute run
    run_1 = await run_service.execute_run(
        request=type("Req", (), happy_req)(),
        custom_client=async_client,
    )
    assert run_1.status.value == "completed"

    # Query run details from API
    run_1_resp = await async_client.get(f"/runs/{run_1.id}")
    assert run_1_resp.status_code == 200
    run_1_data = run_1_resp.json()
    assert run_1_data["status"] == "completed"

    # Query Trace from API
    trace_resp = await async_client.get(f"/runs/{run_1.id}/trace")
    assert trace_resp.status_code == 200
    trace = trace_resp.json()
    assert len(trace) > 0
    assert trace[0]["sequence_number"] == 1

    # Query Evaluation from API
    eval_resp = await async_client.get(f"/runs/{run_1.id}/evaluation")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["success"] is True
    assert eval_data["side_effects"]["is_safe"] is True

    # 3. Execute Failure Scenario Run (Ambiguous Timeout + Unsafe Retry)
    fail_req = {
        "task_id": task_id,
        "scenario_mode": "timeout_after_commit",
        "agent_type": "deterministic",
        "agent_retry_policy": "unsafe_retry",
    }
    run_2 = await run_service.execute_run(
        request=type("Req", (), fail_req)(),
        custom_client=async_client,
    )
    assert run_2.status.value == "failed"

    # Query Diagnosis from API
    diag_resp = await async_client.get(f"/runs/{run_2.id}/diagnosis")
    assert diag_resp.status_code == 200
    diag_data = diag_resp.json()
    assert diag_data is not None
    assert "Ambiguous Operation Outcome" in diag_data["failure_category"]
    assert "Idempotency-Key" in diag_data["recommended_remediation"]

    # 4. Query Reliability Metrics derived from actual runs
    rel_resp = await async_client.get("/reliability")
    assert rel_resp.status_code == 200
    rel_data = rel_resp.json()
    assert rel_data["total_runs"] == 2
    assert rel_data["successful_runs"] == 1
    assert rel_data["failed_runs"] == 1
    assert rel_data["overall_reliability_percentage"] == 50.0
    assert rel_data["by_scenario"]["normal"] == 100.0
    assert rel_data["by_scenario"]["timeout_after_commit"] == 0.0
